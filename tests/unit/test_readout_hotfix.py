"""Bounded host update: preserve existing controls and immutable runtime provenance."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location(
    "readout_hotfix", ROOT / "scripts/apply_fresh_readout_hotfix.py"
)
fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    package, bundle = tmp_path / "original package", tmp_path / "fix package"
    package.mkdir()
    bundle.mkdir()
    old, new = b"old readout\n", b"corrected readout\n"
    monkeypatch.setattr(fix, "BASE_SHA", fix.sha(old))
    (package / fix.TARGET).write_bytes(old)
    (bundle / fix.TARGET).write_bytes(new)
    (package / "matrix.json").write_text("{}")
    (package / "config.yaml").write_text('{"user": "deliberate model edit"}')
    result = package / "results/controls-record"
    result.mkdir(parents=True)
    (result / "manifest.json").write_text('{"status": "completed"}')
    metadata = {
        "id": fix.PATCH_ID,
        "base_source_commit": fix.BASE_COMMIT,
        "operator_source_commit": "a" * 40,
        "old_sha256": fix.BASE_SHA,
        "new_sha256": fix.sha(new),
    }
    (bundle / "patch.json").write_text(json.dumps(metadata))
    release = {
        "source_commit": fix.BASE_COMMIT,
        "image": "nexus:fresh-world-v1",
        "runtime_source_sha256": "c" * 64,
        "files_sha256": {
            fix.TARGET: fix.sha(old),
            "matrix.json": fix.sha(b"{}"),
            "config.yaml": "d" * 64,
        },
        "config_contract_sha256": {"config.yaml": "e" * 64},
    }
    (package / "release.json").write_text(json.dumps(release))
    return package, bundle, release


def test_update_is_idempotent_and_preserves_results_config_and_runtime(setup):
    package, bundle, release = setup
    before = {p.relative_to(package): p.read_bytes() for p in package.rglob("*") if p.is_file()}
    assert fix.apply(package, bundle) == "applied"
    after = json.loads((package / "release.json").read_text())
    assert after["source_commit"] == release["source_commit"]
    assert after["runtime_source_sha256"] == release["runtime_source_sha256"]
    assert after["files_sha256"][fix.TARGET] == fix.sha((bundle / fix.TARGET).read_bytes())
    for path, data in before.items():
        if str(path) not in ("release.json", fix.TARGET):
            assert (package / path).read_bytes() == data
    backup = package / "operator-updates" / fix.PATCH_ID
    assert (backup / "release-before.json").read_bytes() == before[Path("release.json")]
    assert (backup / fix.TARGET).read_bytes() == before[Path(fix.TARGET)]
    snapshot = (package / "release.json").read_bytes()
    assert fix.apply(package, bundle) == "already-applied"
    assert (package / "release.json").read_bytes() == snapshot


@pytest.mark.parametrize("drift", ["source_commit", "readout", "payload", "matrix"])
def test_update_refuses_changed_release_or_payload_without_writing(setup, drift):
    package, bundle, release = setup
    if drift == "source_commit":
        release["source_commit"] = "b" * 40
        (package / "release.json").write_text(json.dumps(release))
    elif drift == "readout":
        (package / fix.TARGET).write_bytes(b"user edit")
    elif drift == "payload":
        (bundle / fix.TARGET).write_bytes(b"bad payload")
    else:
        (package / "matrix.json").write_text('{"changed": true}')
    before = {p: p.read_bytes() for p in package.rglob("*") if p.is_file()}
    with pytest.raises(ValueError):
        fix.apply(package, bundle)
    assert all(p.read_bytes() == data for p, data in before.items())
    assert not (package / "operator-updates").exists()


def test_release_write_failure_restores_original_readout(setup, monkeypatch):
    package, bundle, _ = setup
    old = (package / fix.TARGET).read_bytes()
    original = fix.atomic

    def fail_release(path, data):
        if path.name == "release.json":
            raise OSError("simulated failed release write")
        original(path, data)

    monkeypatch.setattr(fix, "atomic", fail_release)
    with pytest.raises(OSError):
        fix.apply(package, bundle)
    assert (package / fix.TARGET).read_bytes() == old


@pytest.mark.parametrize("fail", [False, True])
def test_resume_skips_completed_astra_tasks_and_stops_on_failure(tmp_path, fail):
    bundle, package = tmp_path / "fix with spaces", tmp_path / "package with spaces"
    bundle.mkdir()
    package.mkdir()
    shutil.copyfile(
        ROOT / "examples/mindtrial/fresh-world-resume-after-readout-fix.sh", bundle / "resume.sh"
    )
    (bundle / "apply.py").write_text("print('fixture update')\n")
    (package / "run.sh").write_text(
        'printf "%s\\n" "$*" >> "$RECORD"\n' + ("exit 23\n" if fail else "exit 0\n")
    )
    log = tmp_path / "commands"
    result = subprocess.run(
        ["bash", str(bundle / "resume.sh"), str(package)],
        check=False,
        capture_output=True,
        env={**os.environ, "PYTHON": sys.executable, "RECORD": str(log)},
    )
    expected = ["--model astra --suite challenges --non-interactive --skip-build"] + [
        f"--model {model} --suite fresh --non-interactive --skip-build"
        for model in ("luna", "flash", "grok")
    ]
    assert log.read_text().splitlines() == expected[: 1 if fail else 4]
    assert result.returncode == (23 if fail else 0)


def test_packaging_reads_the_historical_commit_not_the_worktree(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import package_fresh_readout_hotfix as packer

    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for name in packer.FILES.values():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("historical " + name)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qm", "original patch"], cwd=repo, check=True)
    original = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    for name in packer.FILES.values():
        (repo / name).write_text("later release")
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qam", "later release"], cwd=repo, check=True)
    monkeypatch.setattr(packer, "ROOT", repo)
    monkeypatch.setattr(packer, "PATCH_COMMIT", original)
    output = tmp_path / "patch"
    packer.package(output)
    metadata = json.loads((output / "patch.json").read_bytes())
    assert metadata["operator_source_commit"] == original
    assert metadata["new_sha256"] == fix.sha((output / fix.TARGET).read_bytes())
    assert all((output / name).read_text() == "historical " + path for name, path in packer.FILES.items())
    monkeypatch.setattr(packer, "PATCH_COMMIT", "a" * 40)
    missing = tmp_path / "unavailable"
    with pytest.raises(ValueError, match="fetch commit"):
        packer.package(missing)
    assert not missing.exists()
