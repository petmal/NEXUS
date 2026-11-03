"""Fresh fixtures, control admission and unattended routing; no paid providers."""

import ast
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples/mindtrial"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


fresh = module("fresh_test_qualifier", ROOT / "scripts/fresh_worlds.py")
runner = module("fresh_test_runner", EXAMPLES / "coordination-runner.py")
exporter = module("fresh_test_exporter", ROOT / "scripts/export_fresh_world_configs.py")
PROFILE = runner.FRESH_WORLD


def read(path):
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def pilot():
    return fresh.Pilot.model_validate_json((ROOT / "docs/fresh-world-matrix.json").read_text())


def test_frozen_inventory_covers_each_factor_and_exports_unchanged_anchors(pilot):
    exports = fresh.tasks(pilot)
    assert {s: len(v["task-config"]["tasks"]) for s, v in exports.items()} == {
        "anchor": 6,
        "controls": 4,
        "td": 6,
        "pr-a": 8,
        "pr-b": 8,
    }
    for suite, value in exports.items():
        assert value == read(EXAMPLES / f"nexus-fresh-world-{suite}-tasks.yaml")
    historical = {}
    for path in EXAMPLES.glob("nexus-cross-axis-*-tasks.yaml"):
        historical.update({t["name"]: t for t in read(path)["task-config"]["tasks"]})
    for task in exports["anchor"]["task-config"]["tasks"]:
        assert task == historical[task["name"]]
    for seed in (107, 109):
        assert {
            (c.ontology_options["horizon"], c.ontology_options["coupling"], c.resource)
            for c in pilot.runs
            if c.seed == seed
        } == {
            (h, c, r) for h in ("short", "long") for c in ("independent", "coupled") for r in (1, 2)
        }
    for drift in (
        pilot.runs[:-1],
        tuple(reversed(pilot.runs)),
        (pilot.runs[0].model_copy(update={"seed": 2128}), *pilot.runs[1:]),
    ):
        with pytest.raises(ValueError, match="frozen 26-row"):
            fresh.Pilot(runs=drift)


def test_seed_novelty_uses_behavior_and_historical_missions(pilot):
    assert fresh.fingerprint("model-revision-v1", 2073) == fresh.fingerprint(
        "model-revision-v1", 2128
    )
    evidence = fresh.novelty(pilot)
    assert all(row["distinct_from_history_and_each_other"] for row in evidence.values())
    assert 542 in evidence["compositional-repair-v1"]["historical_seeds_checked"]
    assert all(
        len(row["identities"]) == len(set(row["identities"])) == 2 for row in evidence.values()
    )


def test_configs_preserve_evaluated_presets_and_have_one_model_each():
    contracts = []
    for name, value in exporter.export().items():
        assert read(EXAMPLES / name) == value
        model = name.removeprefix("nexus-fresh-world-").removesuffix("-config.yaml")
        source, provider_name, model_name = exporter.SOURCES[model]
        (provider,) = value["config"]["providers"]
        (run,) = provider["runs"]
        prior = next(
            p for p in read(EXAMPLES / source)["config"]["providers"] if p["name"] == provider_name
        )
        old = next(r for r in prior["runs"] if r["model"] == model_name)
        assert {k: v for k, v in run.items() if k != "name"} == {
            k: v for k, v in old.items() if k != "name"
        }
        assert provider["retry-policy"] == prior["retry-policy"]
        assert not provider["client-config"]["api-key"]
        contracts.append(runner.tool_contract(value, PROFILE.tool_contract_version))
    assert all(c == contracts[0] for c in contracts)


@pytest.fixture(scope="module")
def proof(pilot):
    return fresh.qualified(pilot)


def test_all_worlds_qualify_and_every_contrast_passes(proof):
    assert proof["status"] == "passed"
    assert len(proof["cells"]) == 32
    assert proof["empirical_difficulty_calibrated"] is False
    assert all(all(row["checks"].values()) for row in proof["scientific_contrasts"])
    assert sum(row["kind"] == "resource" for row in proof["scientific_contrasts"]) == 10
    assert len(proof["scientific_contrasts"]) == 30
    hidden = [c for c in proof["cells"] if c["id"] in ("F02", "F04")]
    assert [c["qualification"]["minimum_reading_certificate"] for c in hidden] == [5, 4]
    assert all(c["qualification"]["identifying_query_horizon"] == 5 for c in hidden)


def test_committed_report_recomputes_without_volatile_nested_timing(proof):
    committed = read(ROOT / "docs/research/fresh-world-preflight-2026-11-03.json")
    committed.pop("seconds", None)
    assert committed == proof


@pytest.mark.parametrize(
    "field",
    ["source_sha256", "operator_source_sha256", "history_sha256", "cells", "scientific_contrasts"],
)
def test_stale_or_tampered_proofs_fail_closed(pilot, proof, field):
    altered = copy.deepcopy(proof)
    altered[field] = None
    with pytest.raises(ValueError, match="differs from current"):
        fresh.validate_report(pilot, altered)


@pytest.fixture
def controls(tmp_path, pilot):
    package = tmp_path / "package with spaces"
    package.mkdir()
    shutil.copyfile(EXAMPLES / "summarize-pilot-results.py", package / "summarize_results.py")
    binary = tmp_path / "mindtrial"
    binary.write_bytes(b"test binary")
    config_name = PROFILE.configs[0]
    raw = (EXAMPLES / config_name).read_bytes()
    tasks = fresh.tasks(pilot)["controls"]
    release = {"source_commit": "a" * 40, "runtime_source_sha256": "c" * 64}
    counter = 0

    def record(names=None, mutation=None):
        nonlocal counter
        counter += 1
        chosen = copy.deepcopy(tasks)
        if names is not None:
            chosen["task-config"]["tasks"] = [
                t for t in chosen["task-config"]["tasks"] if t["name"] in names
            ]
        folder = package / f"results/controls-{counter:03}"
        folder.mkdir(parents=True)
        config = json.loads(raw)
        for name, value in (("config.yaml", config), ("tasks.yaml", chosen)):
            runner.write_json(folder / name, value)
        (folder / "input-config.yaml").write_bytes(raw)
        (provider,) = config["config"]["providers"]
        (run,) = provider["runs"]
        records = [
            {
                "Run": run["name"],
                "Provider": provider["name"],
                "Task": t["name"],
                "TraceID": str(i),
                "Kind": "Passed",
                "Evaluation": {"Seed": PROFILE.evaluation_seed},
                "RunConfig": {
                    "Model": run["model"],
                    "ModelParameters": run["model-parameters"],
                    "MaxRequestsPerMinute": run["max-requests-per-minute"],
                    "RetryPolicy": {"InitialDelaySeconds": 30},
                },
                "Details": {"Validation": {"Title": "Valid victory code"}},
            }
            for i, t in enumerate(chosen["task-config"]["tasks"])
        ]
        result = {"Results": {provider["name"]: records}}
        manifest = {
            **release,
            "suite": "controls",
            "status": "completed",
            "exit_code": 0,
            "launcher_exit_code": 0,
            "started_at": f"2026-11-03T00:00:{counter:02}Z",
            "input_config_file": config_name,
            "input_config_sha256": runner.sha256(raw),
            "mindtrial_sha256": runner.sha256(binary.read_bytes()),
            "evaluation_seed": PROFILE.evaluation_seed,
            "selection": {"task_names": [r["Task"] for r in records]},
            "effective_config_sha256": runner.sha256((folder / "config.yaml").read_bytes()),
            "tasks_sha256": runner.sha256((folder / "tasks.yaml").read_bytes()),
        }
        if mutation:
            mutation(manifest, records)
        runner.write_json(folder / "mindtrial.json", result)
        runner.write_json(folder / "manifest.json", manifest)
        return folder

    def admit():
        return runner.control_admission(
            package, release, config_name, raw, binary, tasks, pilot=PROFILE
        )

    return SimpleNamespace(
        package=package,
        binary=binary,
        record=record,
        admit=admit,
        names=[t["name"] for t in tasks["task-config"]["tasks"]],
    )


def test_control_gate_rejects_absence_and_accepts_complete_bound_results(controls):
    with pytest.raises(runner.RunnerError, match="missing or failed"):
        controls.admit()
    folder = controls.record()
    result = controls.admit()
    assert len(result["controls"]) == 4
    assert all(
        c["accepted"]
        and c["manifest"] == str(folder / "manifest.json")
        and len(c["results_sha256"]) == 64
        for c in result["controls"]
    )
    controls.binary.write_bytes(b"new binary")
    with pytest.raises(runner.RunnerError, match="missing or failed"):
        controls.admit()


@pytest.mark.parametrize(
    "drift",
    [
        "failed",
        "receipt",
        "settings",
        "seed",
        "model",
        "duplicate",
        "null_details",
        "incomplete",
        "status",
    ],
)
def test_new_failed_or_invalid_controls_override_old_success(controls, drift):
    controls.record()

    def change(manifest, records):
        if drift == "failed":
            records[0]["Kind"] = "Failed"
        elif drift == "receipt":
            records[0]["Details"]["Validation"]["Title"] = "Invalid victory code"
        elif drift == "settings":
            records[0]["RunConfig"]["MaxRequestsPerMinute"] = 2
        elif drift == "seed":
            records[0]["Evaluation"]["Seed"] = "different"
        elif drift == "model":
            records[0]["RunConfig"]["Model"] = "different"
        elif drift == "duplicate":
            records.append(copy.deepcopy(records[0]))
        elif drift == "null_details":
            records[0]["Details"] = None
        elif drift == "incomplete":
            records.clear()
        elif drift == "status":
            manifest["status"] = "interrupted"

    controls.record(names=controls.names[:1], mutation=change)
    with pytest.raises(runner.RunnerError, match="missing or failed"):
        controls.admit()
    controls.record(names=controls.names[:1])
    assert all(c["accepted"] for c in controls.admit()["controls"])


@pytest.mark.parametrize("field", ["source_commit", "input_config_sha256", "mindtrial_sha256"])
def test_controls_from_other_release_settings_or_binary_cannot_admit(controls, field):
    controls.record(mutation=lambda m, r: m.update({field: "different"}))
    with pytest.raises(runner.RunnerError, match="missing or failed"):
        controls.admit()


def test_corrupted_control_artifact_does_not_fall_back_to_older_success(controls):
    controls.record()
    folder = controls.record()
    (folder / "mindtrial.json").write_text("{")
    with pytest.raises(runner.RunnerError, match="missing or failed"):
        controls.admit()


@pytest.mark.parametrize("packaged", [False, True])
def test_wrappers_self_locate_in_paths_with_spaces(tmp_path, packaged):
    package = tmp_path / "package with spaces"
    package.mkdir()
    script = package / ("run.sh" if packaged else "fresh-world-run.sh")
    shutil.copyfile(EXAMPLES / "fresh-world-run.sh", script)
    shutil.copyfile(
        EXAMPLES / "fresh-world-runner.py",
        package / ("runner.py" if packaged else "fresh-world-runner.py"),
    )
    shutil.copyfile(
        EXAMPLES / "coordination-runner.py",
        package / ("pilot_runner.py" if packaged else "coordination-runner.py"),
    )
    result = subprocess.run(
        ["bash", str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHON": sys.executable},
    )
    assert all(term in result.stdout for term in ("grok", "fresh", "challenges", "--task-id"))
    for path in package.glob("*.py"):
        ast.parse(path.read_text(), feature_version=(3, 12))


@pytest.mark.parametrize("fail_first", [False, True])
def test_run_all_is_unattended_and_stops_on_first_failure(tmp_path, fail_first):
    script = tmp_path / "run-all.sh"
    shutil.copyfile(EXAMPLES / "fresh-world-run-all.sh", script)
    (tmp_path / "run.sh").write_text(
        '#!/bin/bash\nprintf "%s\\n" "$*" >> "$RECORD"\n'
        + ("exit 23\n" if fail_first else "exit 0\n")
    )
    log = tmp_path / "calls.txt"
    result = subprocess.run(
        ["bash", str(script)],
        cwd=ROOT,
        capture_output=True,
        check=False,
        env={**os.environ, "RECORD": str(log)},
    )
    expected = [
        "--model astra --suite anchor --non-interactive",
        "--model all --suite fresh --non-interactive --skip-build",
    ]
    assert result.returncode == (23 if fail_first else 0)
    assert log.read_text().splitlines() == expected[: 1 if fail_first else 2]


def test_main_routes_all_fresh_models_and_records_control_admission(tmp_path, pilot, monkeypatch):
    package = tmp_path / "release"
    package.mkdir()
    configs = exporter.export()
    tasks = fresh.tasks(pilot)
    for name, config in configs.items():
        runner.write_json(package / name, config)
    for suite, value in tasks.items():
        runner.write_json(package / f"nexus-fresh-world-{suite}-tasks.yaml", value)
    shutil.copyfile(EXAMPLES / "summarize-pilot-results.py", package / "summarize_results.py")
    report_path = package / PROFILE.proof_report
    report_path.parent.mkdir()
    shutil.copyfile(ROOT / "docs/research" / report_path.name, report_path)
    release = {
        "source_commit": "a" * 40,
        "runtime_source_sha256": "c" * 64,
        "branch": runner.BRANCH,
        "image": PROFILE.image,
        "files_sha256": {
            p.relative_to(package).as_posix(): runner.sha256(p.read_bytes())
            for p in package.rglob("*")
            if p.is_file()
        },
        "config_contract_sha256": {n: runner.config_contract_sha256(c) for n, c in configs.items()},
    }
    release["tool_contracts"] = {
        n: runner.tool_contract(c, PROFILE.tool_contract_version) for n, c in configs.items()
    }
    runner.write_json(package / "release.json", release)
    binary_dir = tmp_path / "binary"
    binary_dir.mkdir()
    binary = binary_dir / "mindtrial"
    binary.write_text("#!/bin/sh\nexit 99\n")
    binary.chmod(0o755)
    monkeypatch.setenv("MINDTRIAL_DIR", str(binary_dir))
    for key in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "XAI_API_KEY"):
        monkeypatch.setenv(key, "fixture-key-never-written")
    monkeypatch.setattr(
        runner,
        "inspect_image",
        lambda release: {"id": "sha256:" + "b" * 64, "revision": release["source_commit"]},
    )
    monkeypatch.setattr(
        runner,
        "qualify",
        lambda *a, **k: {
            "runtime_source_sha256": release["runtime_source_sha256"],
            "reports": {"fresh-world": {"status": "passed"}},
            "tasks": tasks,
        },
    )
    calls = []

    def execute(command, **kwargs):
        assert command[0] == "./mindtrial"
        assert "--interactive=false" in command
        assert kwargs["stdin"] == subprocess.DEVNULL
        config_path = Path(next(v.split("=", 1)[1] for v in command if v.startswith("-config=")))
        task_path = Path(next(v.split("=", 1)[1] for v in command if v.startswith("-tasks=")))
        config = read(config_path)["config"]
        selected = read(task_path)["task-config"]["tasks"]
        (provider,) = config["providers"]
        (run,) = provider["runs"]
        records = [
            {
                "Provider": provider["name"],
                "Run": run["name"],
                "Task": task["name"],
                "Kind": "Passed",
                "TraceID": f"trace-{i}",
                "Evaluation": {"Seed": PROFILE.evaluation_seed},
                "RunConfig": {
                    "Model": run["model"],
                    "ModelParameters": run["model-parameters"],
                    "MaxRequestsPerMinute": run["max-requests-per-minute"],
                    "RetryPolicy": {"InitialDelaySeconds": 30},
                },
                "Details": {"Validation": {"Title": "Valid victory code"}},
            }
            for i, task in enumerate(selected)
        ]
        runner.write_json(
            config_path.parent / "mindtrial.json", {"Results": {provider["name"]: records}}
        )
        calls.append((run["model"], selected))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    argv = ["--model", "all", "--suite", "fresh", "--non-interactive", "--skip-build"]
    assert runner.main(argv, package_dir=package, pilot=PROFILE) == 0
    assert len(calls) == 16 and sum(len(t) for _, t in calls) == 104
    manifests = [read(p) for p in (package / "results").glob("*/manifest.json")]
    assert len([m for m in manifests if "control_admission" in m]) == 12
    assert all(
        len(m["control_admission"]["controls"]) == 4 for m in manifests if "control_admission" in m
    )
    # Changing the binary makes existing controls ineligible, before a paid challenge.
    binary.write_text("#!/bin/sh\nexit 98\n")
    assert (
        runner.main(
            ["--model", "astra", "--suite", "td", "--non-interactive", "--skip-build"],
            package_dir=package,
            pilot=PROFILE,
        )
        == 1
    )
    assert len(calls) == 16
    # Preflight remains usable without keys, binary or control admission.
    binary.unlink()
    for key in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "XAI_API_KEY"):
        monkeypatch.delenv(key)
    assert (
        runner.main(
            ["--suite", "fresh", "--skip-build", "--preflight-only"],
            package_dir=package,
            pilot=PROFILE,
        )
        == 0
    )
    assert len(calls) == 16


def test_package_includes_bound_proof_matrix_and_working_links(tmp_path, monkeypatch):
    import re
    import zipfile

    packager = module("fresh_test_packager", ROOT / "scripts/package_coordination.py")
    destination = tmp_path / "fresh package"
    # Qualification itself is exercised above and by the real clean-checkout package.
    monkeypatch.setattr(packager, "validate_fresh_world_reports", lambda *args: None)
    monkeypatch.setattr(
        packager.subprocess,
        "check_output",
        lambda command, **kwargs: "" if "status" in command else "a" * 40,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["package", "--output-dir", str(destination), "--runtime-source-sha256", "c" * 64],
    )
    packager.main(pilot_name="fresh-world")
    release = runner.load_release(destination, PROFILE)
    for name in PROFILE.configs:
        runner.load_config(destination, release, name)
    required = {
        "matrix.json",
        "run-all.sh",
        "summarize_results.py",
        "guide.md",
        "reports/fresh-world-preflight-2026-11-03.json",
        "reports/fresh-world-validation-2026-11-03.md",
    }
    assert required <= release["files_sha256"].keys()
    for path in destination.rglob("*.md"):
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", path.read_text()):
            if not target.startswith("https://"):
                assert (path.parent / target).is_file(), (path, target)
    with zipfile.ZipFile(destination.with_suffix(".zip")) as archive:
        assert all(f"{destination.name}/{name}" in archive.namelist() for name in required)


@pytest.mark.parametrize("drift", [None, "operator_source_sha256", "history_sha256", "cells"])
def test_container_proof_must_match_release_report(tmp_path, pilot, proof, monkeypatch, drift):
    tasks = fresh.tasks(pilot)
    for suite, value in tasks.items():
        runner.write_json(tmp_path / f"nexus-fresh-world-{suite}-tasks.yaml", value)
    expected_path = tmp_path / PROFILE.proof_report
    expected_path.parent.mkdir()
    runner.write_json(expected_path, proof)
    actual = copy.deepcopy(proof)
    actual["seconds"] = 999
    if drift:
        actual[drift] = None
    payload = {
        "runtime_source_sha256": proof["source_sha256"],
        "reports": {PROFILE.name: actual},
        "tasks": tasks,
    }
    monkeypatch.setattr(runner, "checked", lambda *a, **k: json.dumps(payload))
    release = {"runtime_source_sha256": proof["source_sha256"]}
    if drift:
        with pytest.raises(runner.RunnerError, match="Recomputed proof differs"):
            runner.qualify(tmp_path, release, {"id": "fixture"}, False, pilot=PROFILE)
    else:
        assert runner.qualify(tmp_path, release, {"id": "fixture"}, False, pilot=PROFILE) == payload
