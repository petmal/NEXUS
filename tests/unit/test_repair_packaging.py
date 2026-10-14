"""Windows build copies preserve exact qualification after newline restoration."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from nexus.ontology.repair import qualification as q

SCRIPTS = Path(__file__).parents[2] / "scripts"


@pytest.fixture
def package(tmp_path, monkeypatch):
    root = tmp_path / "nexus"
    shutil.copytree(
        Path(q.__file__).resolve().parents[2],
        root,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    monkeypatch.setattr(q, "__file__", str(root / "ontology/repair/qualification.py"))
    q.release_matches.cache_clear()
    yield root
    q.release_matches.cache_clear()


def prepare(root):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "prepare_package.py"), str(root)],
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )


def test_crlf_build_copy_restores_exact_package_and_both_public_missions(package):
    original = {p.relative_to(package): p.read_bytes() for p in package.rglob("*") if p.is_file()}
    for relative, content in original.items():
        if relative.suffix in (".py", ".json"):
            (package / relative).write_bytes(content.replace(b"\n", b"\r\n"))
    with pytest.raises(ValueError, match="source CRLF line endings differ"):
        q.require_release()
    prepare(package)
    assert all((package / name).read_bytes() == data for name, data in original.items())
    assert "normalized CRLF in 0 files" in prepare(package).stdout
    q.release_matches.cache_clear()
    q.require_release()
    # Load the prepared package in a fresh process, independently of pytest's imports.
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import runpy,sys; sys.path.insert(0,sys.argv[1]); "
                "runpy.run_path(sys.argv[2],run_name='__main__')"
            ),
            str(package.parent),
            str(SCRIPTS / "preflight_repair.py"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    assert "P0: qualified, won in 14 actions, replay verified" in run.stdout
    assert "P1: qualified, won in 15 actions, replay verified" in run.stdout


@pytest.mark.parametrize(
    "change, message",
    [
        ("source", "source content changed.*ontology/repair/laws.py"),
        ("missing", "source files missing.*ontology/repair/laws.py"),
        ("extra", "source files added.*unexpected.py"),
        ("proof", "query-upper-proof.json content changed"),
        ("proof-crlf", "query-upper-proof.json CRLF line endings differ"),
        ("manifest", "cannot verify qualification"),
        ("manifest-missing", "qualified-release.json"),
        ("witness", "serialized public witness differs"),
    ],
)
def test_diagnostics_reject_every_unqualified_package(package, change, message):
    laws = package / "ontology/repair/laws.py"
    proof = package / "ontology/repair/query-upper-proof.json"
    manifest = package / "ontology/repair/qualified-release.json"
    if change == "source":
        content = laws.read_bytes()
        changed = content.replace(b"value = z", b"value = z + 1")
        assert changed != content
        laws.write_bytes(changed.replace(b"\n", b"\r\n"))
        prepare(package)
    elif change == "missing":
        laws.unlink()
    elif change == "extra":
        (package / "unexpected.py").write_bytes(b"unreviewed = True\n")
    elif change == "proof":
        proof.write_bytes(proof.read_bytes() + b" ")
        prepare(package)
    elif change == "proof-crlf":
        proof.write_bytes(proof.read_bytes().replace(b"\n", b"\r\n"))
    elif change == "manifest":
        manifest.write_bytes(b"{")
    elif change == "manifest-missing":
        manifest.unlink()
    elif change == "witness":
        data = json.loads(manifest.read_text())
        data["witnesses"]["0"] = "changed"
        manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=message):
        q.require_release()


def test_prepare_missing_directory_fails(tmp_path):
    with pytest.raises(subprocess.CalledProcessError):
        prepare(tmp_path / "absent")
