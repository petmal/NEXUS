"""Cross-axis routing, credentials and provenance; no Docker or paid providers."""

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


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_module("cross_axis_shared_runner", EXAMPLES / "coordination-runner.py")
PROFILE = runner.CROSS_AXIS
RUNTIME = "c" * 64
COMMIT = "a" * 40
IMAGE_ID = "sha256:" + "b" * 64
COUNTS = (4, 4, 12, 12, 16, 8)


@pytest.mark.parametrize("packaged", [True, False])
def test_cross_axis_bash_wrapper_self_locates_and_exposes_suite_groups(tmp_path, packaged):
    package = tmp_path / "wrapper package with spaces"
    package.mkdir()
    script = package / ("run.sh" if packaged else "cross-axis-run.sh")
    helper = package / ("runner.py" if packaged else "cross-axis-runner.py")
    shutil.copyfile(EXAMPLES / "cross-axis-run.sh", script)
    shutil.copyfile(EXAMPLES / "cross-axis-runner.py", helper)
    shutil.copyfile(
        EXAMPLES / "coordination-runner.py",
        package / ("pilot_runner.py" if packaged else "coordination-runner.py"),
    )
    result = subprocess.run(
        ["bash", str(script), "--help"],
        cwd=tmp_path,
        env={**os.environ, "PYTHON": sys.executable},
        capture_output=True,
        text=True,
        check=True,
    )
    assert "canary-core" in result.stdout
    assert "followup" in result.stdout
    assert "preflight-only" in result.stdout


def test_shipped_configs_use_selected_provider_keys_and_same_wrapped_tool_contract():
    contracts = []
    for filename, model_count in zip(PROFILE.configs, (3, 2, 2), strict=True):
        config = json.loads((EXAMPLES / filename).read_text())
        providers = config["config"]["providers"]
        assert sum(len(provider["runs"]) for provider in providers) == model_count
        assert all(provider["name"] in runner.PROVIDER_KEYS for provider in providers)
        assert all(not provider["client-config"]["api-key"] for provider in providers)
        tool = config["config"]["tools"][0]
        assert tool["parameters"]["required"] == ["request"]
        assert tool["command"][-2:] == ["--tool-argument", "request"]
        contracts.append(runner.tool_contract(config, PROFILE.tool_contract_version))
    assert contracts[0] == contracts[1] == contracts[2]


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


@pytest.fixture
def cross_axis_setup(tmp_path, monkeypatch):
    package = tmp_path / "package with spaces"
    package.mkdir()
    original = json.loads((EXAMPLES / "nexus-interference-comparison-config.yaml").read_text())
    configs = {}
    for index, name in enumerate(PROFILE.configs):
        config = copy.deepcopy(original)
        for section in ("tools", "services", "validators"):
            for entry in config["config"][section]:
                entry["image"] = PROFILE.image
        config["config"]["tools"][0]["command"].extend(["--tool-argument", "request"])
        if index != 1:
            config["config"]["providers"].append(
                {
                    "name": "google",
                    "client-config": {"api-key": ""},
                    "retry-policy": {"max-retry-attempts": 0},
                    "runs": [
                        {
                            "name": "Gemini Flash",
                            "model": "gemini-3.8-flash",
                            "disabled": False,
                            "max-requests-per-minute": 3,
                            "model-parameters": {"thinking-level": "high"},
                        }
                    ],
                }
            )
        if index == 2:
            config["config"]["providers"][0]["runs"].pop(0)
        configs[name] = config
        dump(package / name, config)
    tasks = {}
    for suite, count in zip(PROFILE.suites, COUNTS, strict=True):
        tasks[suite] = {"task-config": {"tasks": [{"name": f"{suite}-{i}"} for i in range(count)]}}
        dump(package / f"nexus-cross-axis-{suite}-tasks.yaml", tasks[suite])
    release = {
        "source_commit": COMMIT,
        "branch": runner.BRANCH,
        "image": PROFILE.image,
        "runtime_source_sha256": RUNTIME,
        "config_contract_sha256": {
            name: runner.config_contract_sha256(config) for name, config in configs.items()
        },
        "tool_contracts": {
            name: runner.tool_contract(config, PROFILE.tool_contract_version)
            for name, config in configs.items()
        },
        "files_sha256": {p.name: runner.sha256(p.read_bytes()) for p in package.iterdir()},
    }
    dump(package / "release.json", release)
    mindtrial = tmp_path / "MindTrial with spaces"
    mindtrial.mkdir()
    binary = mindtrial / "mindtrial"
    binary.write_text("#!/bin/sh\nexit 99\n")
    binary.chmod(0o755)
    monkeypatch.setenv("MINDTRIAL_DIR", str(mindtrial))
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-secret")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test-secret")
    state = {
        "package": package,
        "release": release,
        "configs": configs,
        "image_id": IMAGE_ID,
        "calls": [],
        "payload": {
            "runtime_source_sha256": RUNTIME,
            "reports": {"cross-axis": {"status": "passed"}},
            "tasks": tasks,
        },
    }

    def fake_run(command, **kwargs):
        state["calls"].append((command, kwargs))
        if command[:3] == ["docker", "image", "inspect"]:
            return subprocess.CompletedProcess(
                command,
                0,
                json.dumps(
                    {
                        "Id": state["image_id"],
                        "Config": {"Labels": {"org.opencontainers.image.revision": COMMIT}},
                    }
                ),
                "",
            )
        if command[:2] == ["docker", "run"]:
            assert command[-1] == PROFILE.preflight_script
            assert command[command.index("--network") + 1] == "none"
            assert not {"--mount", "-v", "--env", "-e"} & set(command)
            return subprocess.CompletedProcess(command, 0, json.dumps(state["payload"]), "")
        if command[0] == "./mindtrial":
            assert kwargs == {"cwd": mindtrial, "check": False}
            return subprocess.CompletedProcess(command, 0)
        raise AssertionError(f"Unexpected subprocess: {command}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    return state


def invoke(state, *args):
    return runner.main(["--skip-build", *args], package_dir=state["package"], pilot=PROFILE)


def manifests(state):
    return [
        json.loads(path.read_text())
        for path in sorted((state["package"] / "results").glob("*/manifest.json"))
    ]


@pytest.mark.parametrize(
    ("selection", "suites"),
    [
        (None, PROFILE.suites[:2]),
        ("canary", PROFILE.suites[:2]),
        ("rerun", PROFILE.suites[2:4]),
        ("smoke", PROFILE.suites[4:]),
        ("followup", PROFILE.suites[2:]),
        *((suite, (suite,)) for suite in PROFILE.suites),
    ],
)
def test_groups_select_each_suite_once_and_route_configs(cross_axis_setup, selection, suites):
    state = cross_axis_setup
    args = [] if selection is None else ["--suite", selection]
    assert invoke(state, *args) == 0
    records = manifests(state)
    assert sorted(r["suite"] for r in records) == sorted(suites)
    for record in records:
        assert record["input_config_file"] == runner.config_for_suite(record["suite"], PROFILE)
        assert (
            record["tool_contract"]
            == state["release"]["tool_contracts"][record["input_config_file"]]
        )
        assert record["tool_contract"]["provider_wire_captured"] is False
        assert record["evaluation_seed"] == "nexus-cross-axis-pilot-v1"
    assert sum(command[:2] == ["docker", "run"] for command, _ in state["calls"]) == 1


@pytest.mark.parametrize("image_id", [IMAGE_ID, "d" * 64])
def test_all_has_56_distinct_conditions_and_120_attempts(cross_axis_setup, image_id):
    state = cross_axis_setup
    state["image_id"] = image_id
    assert invoke(state, "--suite", "all") == 0
    names, attempts = [], 0
    records = manifests(state)
    assert len(records) == 6
    for record in records:
        directory = Path(record["output_dir"])
        config = json.loads((directory / "config.yaml").read_text())["config"]
        tasks = json.loads((directory / "tasks.yaml").read_text())["task-config"]["tasks"]
        names.extend(task["name"] for task in tasks)
        attempts += len(tasks) * sum(len(p["runs"]) for p in config["providers"])
        assert all(
            entry["image"] == image_id
            for section in ("tools", "services", "validators")
            for entry in config[section]
        )
    assert len(names) == len(set(names)) == 56
    assert attempts == 120


def test_rerun_only_does_not_require_google_key(cross_axis_setup, monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY")
    assert invoke(cross_axis_setup, "--suite", "rerun") == 0


@pytest.mark.parametrize("variable", ["OPENAI_API_KEY", "GOOGLE_API_KEY"])
def test_canary_requires_each_selected_provider_key_before_docker(
    cross_axis_setup, monkeypatch, variable, capsys
):
    monkeypatch.delenv(variable)
    assert invoke(cross_axis_setup) == 1
    assert variable in capsys.readouterr().err
    assert not cross_axis_setup["calls"]


def test_preflight_needs_no_keys_and_checks_unselected_smoke_export(cross_axis_setup, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    monkeypatch.delenv("GOOGLE_API_KEY")
    assert invoke(cross_axis_setup, "--preflight-only") == 0
    assert len(cross_axis_setup["payload"]["tasks"]) == 6
    (record,) = manifests(cross_axis_setup)
    assert record["command"] is None
    assert record["input_configs"][PROFILE.configs[0]]["tool_contract"]["scope"] == "configuration"
    cross_axis_setup["payload"]["tasks"]["smoke-td"]["task-config"]["tasks"].pop()
    assert invoke(cross_axis_setup, "--preflight-only") == 1
    assert all(command[0] != "./mindtrial" for command, _ in cross_axis_setup["calls"])


@pytest.mark.parametrize(
    "failure", ["missing-contract", "wire-claim", "tool-digest", "runtime", "qualification"]
)
def test_provenance_failures_block_live_runs(cross_axis_setup, failure):
    state = cross_axis_setup
    if failure == "missing-contract":
        state["release"].pop("tool_contracts")
    elif failure == "wire-claim":
        state["release"]["tool_contracts"][PROFILE.configs[0]]["provider_wire_captured"] = True
    elif failure == "tool-digest":
        state["release"]["tool_contracts"][PROFILE.configs[0]]["sha256"] = "d" * 64
    elif failure == "runtime":
        state["payload"]["runtime_source_sha256"] = "d" * 64
    else:
        state["payload"]["reports"]["cross-axis"]["status"] = "failed"
    dump(state["package"] / "release.json", state["release"])
    assert invoke(state) == 1
    assert all(command[0] != "./mindtrial" for command, _ in state["calls"])


def test_model_rate_effort_edit_preserves_tool_contract_but_disabled_edit_is_blocked(
    cross_axis_setup,
):
    state = cross_axis_setup
    filename = PROFILE.configs[0]
    config = state["configs"][filename]
    run = config["config"]["providers"][1]["runs"][0]
    run.update(
        model="operator-selected-model",
        **{"model-parameters": {"thinking-level": "low"}, "max-requests-per-minute": 10},
    )
    dump(state["package"] / filename, config)
    assert invoke(state) == 0
    assert all(record["input_config_matches_release"] is False for record in manifests(state))
    run["disabled"] = True
    dump(state["package"] / filename, config)
    assert invoke(state) == 1


@pytest.mark.parametrize("embedded", ["api-key", "environment"])
def test_google_credentials_are_never_persisted_or_echoed(cross_axis_setup, embedded, capsys):
    state = cross_axis_setup
    config = state["configs"][PROFILE.configs[0]]
    if embedded == "api-key":
        config["config"]["providers"][1]["client-config"]["api-key"] = "embedded-private-key"
    else:
        config["config"]["providers"][1]["runs"][0]["name"] = "google-test-secret"
    dump(state["package"] / PROFILE.configs[0], config)
    assert invoke(state) == 1
    output = capsys.readouterr()
    assert "google-test-secret" not in output.err + output.out
    assert "embedded-private-key" not in output.err + output.out
    assert not (state["package"] / "results").exists()


@pytest.fixture
def package_setup(cross_axis_setup, tmp_path, monkeypatch):
    packager = load_module("cross_axis_packager", ROOT / "scripts/package_coordination.py")
    source = tmp_path / "source"
    examples = source / "examples/mindtrial"
    examples.mkdir(parents=True)
    for name in (
        "coordination-runner.py",
        "cross-axis-runner.py",
        "cross-axis-run.sh",
        "cross-axis-run.md",
        "summarize-pilot-results.py",
    ):
        shutil.copyfile(EXAMPLES / name, examples / name)
    for path in cross_axis_setup["package"].iterdir():
        if path.suffix == ".yaml":
            shutil.copyfile(path, examples / path.name)
    research = source / "docs/research"
    research.mkdir(parents=True)
    (source / "docs/cross-axis-guide.md").write_text("Cross-axis guide\n")
    (research / "cross-axis-validation-2026-10-29.md").write_text("Validation record\n")
    code = source / "src/nexus/example.py"
    code.parent.mkdir(parents=True)
    code.write_text("# Source binding fixture\n")
    dump(source / "docs/cross-axis-matrix.json", {"runs": []})
    report = {"source_sha256": RUNTIME, "sources": {"example.py": runner.sha256(code.read_bytes())}}
    report_path = research / "cross-axis-preflight-2026-10-29.json"
    dump(report_path, report)
    validation_calls = []

    def validate_report(pilot, value):
        validation_calls.append((pilot, value))
        if value.get("reject"):
            raise ValueError("cross-axis proof inventory is incomplete")

    monkeypatch.setitem(
        sys.modules,
        "nexus.evaluation.cross_axis",
        SimpleNamespace(
            Pilot=SimpleNamespace(model_validate_json=json.loads), validate_report=validate_report
        ),
    )
    monkeypatch.setattr(packager, "ROOT", source)
    monkeypatch.setattr(
        packager.subprocess,
        "check_output",
        lambda command, **_: "" if command[-1] == "--porcelain" else COMMIT + "\n",
    )
    destination = tmp_path / "new release"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "package_cross_axis.py",
            "--output-dir",
            str(destination),
            "--runtime-source-sha256",
            RUNTIME,
        ],
    )
    return packager, source, destination, report_path, validation_calls


def test_package_validates_new_report_and_pins_all_routed_configs(package_setup):
    packager, _, destination, _, calls = package_setup
    packager.main("cross-axis")
    assert len(calls) == 1
    release = runner.load_release(destination, PROFILE)
    assert set(release["tool_contracts"]) == set(PROFILE.configs)
    assert (destination / "guide.md").is_file()
    assert (destination / "summarize_results.py").is_file()
    assert len(list(destination.glob("nexus-cross-axis-*-tasks.yaml"))) == 6
    assert {p.name for p in (destination / "reports").iterdir()} == {
        "cross-axis-preflight-2026-10-29.json",
        "cross-axis-validation-2026-10-29.md",
    }
    assert destination.with_suffix(".zip").is_file()


@pytest.mark.parametrize("failure", ["source", "runtime", "mechanical-proof"])
def test_package_rejects_stale_or_unqualified_report_before_copy(package_setup, failure):
    packager, _, destination, path, calls = package_setup
    report = json.loads(path.read_text())
    if failure == "source":
        report["sources"]["example.py"] = "d" * 64
    elif failure == "runtime":
        report["source_sha256"] = "d" * 64
    else:
        report["reject"] = True
    dump(path, report)
    with pytest.raises(SystemExit):
        packager.main("cross-axis")
    assert not destination.exists()
    assert len(calls) == (1 if failure == "mechanical-proof" else 0)
