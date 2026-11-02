"""Release boundary tests for the five-model screen; never call paid providers."""

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
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


runner = module("capability_shared_runner", EXAMPLES / "coordination-runner.py")
exporter = module("capability_exporter", ROOT / "scripts/export_capability_smoke.py")
PROFILE = runner.CAPABILITY_SMOKE
IMAGE = {"id": "sha256:" + "b" * 64}


def read(path):
    return json.loads(path.read_text())


def test_selected_rows_are_disjoint_exact_historical_task_objects():
    exports = {
        suite: read(EXAMPLES / f"nexus-cross-axis-{suite}-tasks.yaml")
        for suite in runner.CROSS_AXIS.suites
    }
    chosen = runner.select_capability_tasks(exports)
    old = {t["name"]: t for value in exports.values() for t in value["task-config"]["tasks"]}
    names = [t["name"] for v in chosen.values() for t in v["task-config"]["tasks"]]
    assert len(names) == len(set(names)) == 16
    assert [t["name"] for t in chosen["controls"]["task-config"]["tasks"]] == [
        "NEXUS smoke-S05",
        "NEXUS smoke-S21",
    ]
    assert set(names) == {
        f"NEXUS smoke-{s}"
        for s in (
            "S01",
            "S02",
            "S03",
            "S05",
            "S08",
            "S21",
            "S22",
            "S23",
            "S24",
            "S13",
            "S16",
            "S17",
        )
    } | {f"NEXUS interference-{s}" for s in ("09", "11", "25", "27")}
    for suite, value in chosen.items():
        assert value == read(EXAMPLES / f"nexus-capability-smoke-{suite}-tasks.yaml")
        assert value["task-config"]["max-turns"] == 650
        assert value["task-config"]["tool-selector"]["tools"] == [
            {"name": "nexus", "max-calls": 600}
        ]
        for task in value["task-config"]["tasks"]:
            assert task == old[task["name"]]
    # Missing, duplicated or differently limited source exports fail closed.
    changed = copy.deepcopy(exports)
    changed["smoke-pr"]["task-config"]["max-turns"] = 1
    with pytest.raises(ValueError, match="identical harness"):
        runner.select_capability_tasks(changed)
    exports["canary-core"]["task-config"]["tasks"].pop(0)
    with pytest.raises(ValueError, match="exactly one"):
        runner.select_capability_tasks(exports)


def test_configs_reproduce_export_and_preserve_player_contract():
    for filename, expected in exporter.export().items():
        assert expected == read(EXAMPLES / filename)
    old = read(EXAMPLES / "nexus-cross-axis-smoke-config.yaml")
    contract = runner.tool_contract(old, PROFILE.tool_contract_version)
    for filename in PROFILE.configs:
        config = read(EXAMPLES / filename)
        assert runner.tool_contract(config, PROFILE.tool_contract_version) == contract
        (provider,) = config["config"]["providers"]
        (run,) = provider["runs"]
        assert provider["client-config"]["api-key"] == ""
        assert provider["retry-policy"]["max-retry-attempts"] == 0
        assert not run["disabled"]
        assert not run["model-parameters"].get("server-tools")
        assert run.get("disable-structured-output", False) is (
            run["model"] in ("z-ai/glm-5.2", "minimax/minimax-m3")
        )
        assert "disable-structured-output" not in run["model-parameters"]
        if provider["name"] == "openrouter":
            assert run["model-parameters"]["provider"] == {
                "require_parameters": True,
                "allow_fallbacks": False,
            }
    assert PROFILE.evaluation_seed == "nexus-cross-axis-pilot-v1"
    ast.parse(PROFILE.preflight_script, feature_version=(3, 12))


@pytest.fixture
def setup_package(tmp_path, monkeypatch):
    package = tmp_path / "package with spaces"
    package.mkdir()
    for name in PROFILE.configs:
        shutil.copyfile(EXAMPLES / name, package / name)
    for suite in PROFILE.suites:
        name = f"nexus-capability-smoke-{suite}-tasks.yaml"
        shutil.copyfile(EXAMPLES / name, package / name)
    release = {
        "source_commit": "a" * 40,
        "branch": runner.BRANCH,
        "image": PROFILE.image,
        "runtime_source_sha256": "c" * 64,
        "files_sha256": {p.name: runner.sha256(p.read_bytes()) for p in package.iterdir()},
        "config_contract_sha256": {
            n: runner.config_contract_sha256(read(package / n)) for n in PROFILE.configs
        },
        "tool_contracts": {
            n: runner.tool_contract(read(package / n), PROFILE.tool_contract_version)
            for n in PROFILE.configs
        },
    }
    runner.write_json(package / "release.json", release)
    preflight = {
        "runtime_source_sha256": "c" * 64,
        "reports": {"capability-smoke": {"status": "passed"}},
        "tasks": {
            s: read(package / f"nexus-capability-smoke-{s}-tasks.yaml") for s in PROFILE.suites
        },
    }
    binary_dir = tmp_path / "MindTrial with spaces"
    binary_dir.mkdir()
    binary = binary_dir / "mindtrial"
    binary.write_text("fixture binary, never executed")
    binary.chmod(0o700)
    monkeypatch.setenv("MINDTRIAL_DIR", str(binary_dir))
    for key in runner.PROVIDER_KEYS.values():
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(runner, "build_image", lambda *a: None)
    monkeypatch.setattr(runner, "inspect_image", lambda *a: IMAGE)
    monkeypatch.setattr(runner, "qualify", lambda *a, **kw: copy.deepcopy(preflight))
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", run)
    return package, release, preflight, calls


@pytest.mark.parametrize(
    "model,key",
    [
        ("glm", "OPENROUTER_API_KEY"),
        ("muse", "OPENROUTER_API_KEY"),
        ("minimax", "OPENROUTER_API_KEY"),
        ("mistral", "MISTRAL_API_KEY"),
        ("grok", "XAI_API_KEY"),
    ],
)
def test_selected_model_only_requires_its_key_and_records_exact_config(
    setup_package, monkeypatch, model, key
):
    package, release, _, calls = setup_package
    monkeypatch.setenv(key, "fixture-value-that-must-not-be-copied")
    assert (
        runner.main(
            ["--model", model, "--suite", "all", "--skip-build"], package_dir=package, pilot=PROFILE
        )
        == 0
    )
    assert len(calls) == 2
    manifests = [read(p) for p in (package / "results").glob("*/manifest.json")]
    assert {m["suite"] for m in manifests} == {"controls", "screen"}
    expected_name = dict(PROFILE.model_configs)[model]
    for m in manifests:
        assert m["input_config_file"] == expected_name
        assert m["input_config_matches_release"] is True
        assert m["evaluation_seed"] == "nexus-cross-axis-pilot-v1"
        directory = Path(m["output_dir"])
        effective = read(directory / "config.yaml")
        assert len(effective["config"]["providers"]) == 1
        assert runner.sha256((directory / "tasks.yaml").read_bytes()) == m["tasks_sha256"]
        assert m["tool_contract"] == release["tool_contracts"][expected_name]
        assert (
            "fixture-value-that-must-not-be-copied" not in (directory / "config.yaml").read_text()
        )
        assert "--interactive=true" in m["command"]
        assert all(
            item["image"] == IMAGE["id"]
            for section in ("tools", "services", "validators")
            for item in effective["config"][section]
        )


def test_default_controls_all_models_and_no_followup(setup_package, monkeypatch):
    package, _, _, calls = setup_package
    for key in ("OPENROUTER_API_KEY", "MISTRAL_API_KEY", "XAI_API_KEY"):
        monkeypatch.setenv(key, "dummy-distinct-fixture-key")
    assert runner.main(["--skip-build"], package_dir=package, pilot=PROFILE) == 0
    assert len(calls) == 5
    manifests = [read(p) for p in (package / "results").glob("*/manifest.json")]
    assert {m["input_config_file"] for m in manifests} == set(PROFILE.configs)
    assert {m["suite"] for m in manifests} == {"controls"}
    assert (
        sum(
            len(read(Path(m["output_dir"]) / "tasks.yaml")["task-config"]["tasks"])
            for m in manifests
        )
        == 10
    )


def test_preflight_needs_no_keys_and_edited_tasks_refused(setup_package):
    package, _, _, calls = setup_package
    assert (
        runner.main(["--preflight-only", "--skip-build"], package_dir=package, pilot=PROFILE) == 0
    )
    assert calls == []
    task = package / "nexus-capability-smoke-screen-tasks.yaml"
    task.write_text(task.read_text().replace('"seed": "229"', '"seed": "230"', 1))
    with pytest.raises(runner.RunnerError, match="checksum mismatch"):
        runner.load_release(package, PROFILE)


def test_packaged_bash_entry_point_accepts_model_selector(tmp_path):
    for source, target in (
        ("capability-smoke-run.sh", "run.sh"),
        ("capability-smoke-runner.py", "runner.py"),
        ("coordination-runner.py", "pilot_runner.py"),
    ):
        shutil.copyfile(EXAMPLES / source, tmp_path / target)
    result = subprocess.run(
        ["bash", str(tmp_path / "run.sh"), "--help"],
        env={**os.environ, "PYTHON": sys.executable},
        capture_output=True,
        text=True,
        check=True,
    )
    assert "{all,glm,muse,minimax,mistral,grok}" in result.stdout
    assert "{controls,screen,all}" in result.stdout


def test_package_contains_verified_files_and_working_local_links(tmp_path, monkeypatch):
    packager = module("capability_packager", ROOT / "scripts/package_coordination.py")
    destination = tmp_path / "new package"
    # The full proof is tested separately; isolate filesystem release assembly here.
    monkeypatch.setattr(packager, "validate_cross_axis_reports", lambda *args: None)
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
    packager.main(pilot_name="capability-smoke")
    release = runner.load_release(destination, PROFILE)
    for name in PROFILE.configs:
        runner.load_config(destination, release, name)
    assert (destination.parent / (destination.name + ".zip")).is_file()
    assert "(reports/smoke-findings-2026-10-31.md)" in (destination / "guide.md").read_text()
    assert "(matrix.json)" in (destination / "guide.md").read_text()
    assert "(followup-matrix.md)" in (destination / "guide.md").read_text()
    assert (
        "(reports/smaller-model-synthesis-2026-11-01.md)"
        in (destination / "followup-matrix.md").read_text()
    )
    assert "(../guide.md)" in (destination / "reports/smoke-findings-2026-10-31.md").read_text()
    assert set(PROFILE.configs) <= release["files_sha256"].keys()
    assert read(destination / "matrix.json")["attempts"]["total"] == 80


def write_mock_results(command, *, partial=False, kind="Passed"):
    config_path = Path(next(v.split("=", 1)[1] for v in command if v.startswith("-config=")))
    task_path = Path(next(v.split("=", 1)[1] for v in command if v.startswith("-tasks=")))
    config = read(config_path)["config"]
    tasks = read(task_path)["task-config"]["tasks"]
    result = {}
    for p in config["providers"]:
        result[p["name"]] = [
            {
                "Run": run["name"],
                "Task": task["name"],
                "Kind": kind,
                "TraceID": f"{p['name']}-{i}-{j}",
            }
            for i, run in enumerate(p["runs"])
            for j, task in enumerate(tasks[:1] if partial else tasks)
        ]
    runner.write_json(config_path.parent / "mindtrial.json", {"Results": result})


@pytest.mark.parametrize("kind", ["Passed", "Failed", "Error"])
def test_unattended_mode_runs_both_groups_and_checks_coverage(setup_package, monkeypatch, kind):
    package, _, _, calls = setup_package
    monkeypatch.setenv("XAI_API_KEY", "fixture-grok-key")

    def execute(command, **kwargs):
        calls.append((command, kwargs))
        assert "--interactive=false" in command
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert "stdout" not in kwargs and "stderr" not in kwargs
        write_mock_results(command, kind=kind)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    assert (
        runner.main(
            ["--model", "grok", "--suite", "all", "--non-interactive", "--skip-build"],
            package_dir=package,
            pilot=PROFILE,
        )
        == 0
    )
    assert len(calls) == 2
    manifests = [read(p) for p in (package / "results").glob("*/manifest.json")]
    assert {m["suite"] for m in manifests} == {"controls", "screen"}
    for m in manifests:
        assert m["interactive"] is False
        assert m["result_coverage"]["complete"]
        assert m["status"] == "completed"
        assert m["exit_code"] == m["launcher_exit_code"] == 0


@pytest.mark.parametrize("mode", ["missing", "empty", "partial", "invalid"])
def test_zero_exit_without_complete_results_stops_unattended_batch(
    setup_package, monkeypatch, mode
):
    package, _, _, calls = setup_package
    monkeypatch.setenv("XAI_API_KEY", "fixture-grok-key")

    def execute(command, **kwargs):
        calls.append((command, kwargs))
        config_path = Path(next(v.split("=", 1)[1] for v in command if v.startswith("-config=")))
        if mode == "partial":
            write_mock_results(command, partial=True)
        elif mode != "missing":
            (config_path.parent / "mindtrial.json").write_text("" if mode == "empty" else "{")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    assert (
        runner.main(
            ["--model", "grok", "--suite", "all", "--non-interactive", "--skip-build"],
            package_dir=package,
            pilot=PROFILE,
        )
        == 2
    )
    assert len(calls) == 1
    m = read(next((package / "results").glob("*/manifest.json")))
    assert m["status"] == "incomplete_results" and not m["result_coverage"]["complete"]
    assert m["exit_code"] == 0 and m["launcher_exit_code"] == 2


def test_interactive_mode_preserves_manual_selection_and_terminal_input(setup_package, monkeypatch):
    package, _, _, calls = setup_package
    monkeypatch.setenv("XAI_API_KEY", "fixture-grok-key")
    assert (
        runner.main(
            ["--model", "grok", "--interactive", "--skip-build"], package_dir=package, pilot=PROFILE
        )
        == 0
    )
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert "--interactive=true" in command and "stdin" not in kwargs
    m = read(next((package / "results").glob("*/manifest.json")))
    assert m["interactive"] is True and "result_coverage" not in m


def test_modes_are_mutually_exclusive():
    with pytest.raises(SystemExit):
        runner.main(["--interactive", "--non-interactive"], pilot=PROFILE)


def test_packaged_host_scripts_support_python_312():
    for name in (
        "coordination-runner.py",
        "capability-smoke-runner.py",
        "summarize-pilot-results.py",
    ):
        ast.parse((EXAMPLES / name).read_text(), feature_version=(3, 12))


def test_selected_unattended_repetitions_preserve_tasks_and_complete_only_selected_rows(
    setup_package, monkeypatch
):
    package, _, preflight, calls = setup_package
    monkeypatch.setenv("OPENROUTER_API_KEY", "fixture-key")

    def execute(command, **kwargs):
        calls.append((command, kwargs))
        write_mock_results(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    assert (
        runner.main(
            [
                "--model",
                "glm",
                "--suite",
                "all",
                "--task-id",
                "11",
                "--task-id",
                "27",
                "--repeat",
                "2",
                "--non-interactive",
                "--skip-build",
            ],
            package_dir=package,
            pilot=PROFILE,
        )
        == 0
    )
    assert len(calls) == 2
    manifests = [read(p) for p in (package / "results").glob("*/manifest.json")]
    assert sorted(m["repetition"]["index"] for m in manifests) == [1, 2]
    expected = [
        t
        for t in preflight["tasks"]["screen"]["task-config"]["tasks"]
        if t["name"].endswith(("-11", "-27"))
    ]
    for m in manifests:
        assert m["suite"] == "screen" and m["repetition"]["count"] == 2
        assert m["result_coverage"]["expected"] == m["result_coverage"]["recorded"] == 2
        assert m["result_coverage"]["complete"]
        output = Path(m["output_dir"])
        assert read(output / "tasks.yaml")["task-config"]["tasks"] == expected
        assert read(output / "preflight.json") == preflight
        assert m["selection"]["task_names"] == [t["name"] for t in expected]


@pytest.mark.parametrize("ids", [["missing"], ["11", "11"], ["11", "NEXUS interference-11"]])
def test_bad_selection_stops_before_any_external_call(setup_package, ids):
    package, _, _, calls = setup_package
    args = ["--model", "glm", "--suite", "screen", "--preflight-only"]
    for row in ids:
        args.extend(["--task-id", row])
    assert runner.main(args, package_dir=package, pilot=PROFILE) == 1
    assert not calls and not (package / "results").exists()


def test_selection_rejects_ambiguous_suffix_and_never_changes_source():
    exports = {"a": {"task-config": {"tasks": [{"name": "world-11"}, {"name": "other-11"}]}}}
    before = copy.deepcopy(exports)
    with pytest.raises(runner.RunnerError, match="exactly one"):
        runner.select_task_ids(exports, ("a",), ["11"])
    selected = runner.select_task_ids(exports, ("a",), ["world-11"])
    selected["a"]["task-config"]["tasks"][0]["name"] = "changed"
    assert exports == before


def test_repetition_count_must_be_positive():
    with pytest.raises(SystemExit):
        runner.main(["--repeat", "0"], pilot=PROFILE)


@pytest.mark.parametrize("mode", ["duplicate", "unexpected", "invalid_identity", "duplicate_trace"])
def test_result_coverage_rejects_ambiguous_records(tmp_path, mode):
    config = {"config": {"providers": [{"name": "p", "runs": [{"name": "r"}]}]}}
    tasks = {"task-config": {"tasks": [{"name": "t"}]}}
    record = {"Run": "r", "Task": "t", "Kind": "Passed", "TraceID": "one"}
    records = [record]
    if mode in ("duplicate", "duplicate_trace"):
        records.append({**record, "TraceID": "two" if mode == "duplicate" else "one"})
    elif mode == "unexpected":
        record["Task"] = "other"
    else:
        record["Run"] = 42
    runner.write_json(tmp_path / "mindtrial.json", {"Results": {"p": records}})
    assert not runner.result_coverage(tmp_path, config, tasks)["complete"]
