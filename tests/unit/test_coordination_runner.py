"""Exercise the launcher at real subprocess boundaries; never call a live model."""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).parents[2]
RUNNER = ROOT / "examples/mindtrial/coordination-runner.py"
LAUNCHER = ROOT / "examples/mindtrial/coordination-run.sh"
SPEC = importlib.util.spec_from_file_location("coordination_runner", RUNNER)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
IMAGE_ID = "sha256:" + "b" * 64
BARE_IMAGE_ID = "3ec5418c338244066307c55c3e76c494315edc95733a8ccfc4644717b9ffdd3d"
RUNTIME = "c" * 64
REAL_RUN = subprocess.run


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


@pytest.fixture
def setup(tmp_path, monkeypatch):
    home = tmp_path / "home with spaces"
    package = home / "Downloads/pilot package"
    package.mkdir(parents=True)
    repository = home / "Go-Projects/NEXUS"
    repository.mkdir(parents=True)
    for arguments in (
        ["init", "-b", runner.BRANCH],
        ["config", "user.email", "runner-test@example.invalid"],
        ["config", "user.name", "Runner test"],
    ):
        REAL_RUN(["git", "-C", str(repository), *arguments], check=True, capture_output=True)
    (repository / "Dockerfile").write_text("FROM scratch\nCOPY marker /marker\n")
    (repository / "marker").write_text("committed bytes\n")
    for arguments in (["add", "."], ["commit", "-m", "fixture"]):
        REAL_RUN(["git", "-C", str(repository), *arguments], check=True, capture_output=True)
    commit = REAL_RUN(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (repository / "marker").write_text("uncommitted user work\n")
    (repository / "untracked").write_text("untracked user work\n")
    mindtrial = home / "MindTrial"
    mindtrial.mkdir()
    binary = mindtrial / "mindtrial"
    binary.write_text("#!/bin/sh\nexit 99\n")
    binary.chmod(0o755)
    for name in runner.CONFIGS:
        shutil.copyfile(ROOT / "examples/mindtrial" / name, package / name)
    tasks = {}
    for suite, count in (("core", 16), ("slack", 16), ("spatial", 8), ("repeat", 10)):
        tasks[suite] = {
            "task-config": {"tasks": [{"name": f"{suite}-{index}"} for index in range(count)]}
        }
        dump(package / f"nexus-coordination-{suite}-tasks.yaml", tasks[suite])
    shutil.copyfile(LAUNCHER, package / "run.sh")
    shutil.copyfile(RUNNER, package / "runner.py")
    (package / "run.sh").chmod(0o755)
    release = {
        "source_commit": commit,
        "branch": runner.BRANCH,
        "image": runner.IMAGE,
        "runtime_source_sha256": RUNTIME,
        "files_sha256": {p.name: runner.sha256(p.read_bytes()) for p in package.iterdir()},
        "config_contract_sha256": {
            name: runner.config_contract_sha256(json.loads((package / name).read_text()))
            for name in runner.CONFIGS
        },
    }
    dump(package / "release.json", release)
    payload = {
        "runtime_source_sha256": RUNTIME,
        "reports": {"coordination": {"status": "passed"}, "planning_repeat": {"status": "passed"}},
        "tasks": copy.deepcopy(tasks),
    }
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-do-not-persist")
    monkeypatch.delenv("NEXUS_REPO", raising=False)
    monkeypatch.delenv("MINDTRIAL_DIR", raising=False)
    elsewhere = tmp_path / "unrelated working directory"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    state: dict[str, Any] = {
        "home": home,
        "package": package,
        "repository": repository,
        "mindtrial": mindtrial,
        "release": release,
        "payload": payload,
        "calls": [],
        "revision": commit,
        "image_id": IMAGE_ID,
        "live_status": 0,
        "git_failure": False,
    }

    def fake_run(command, **kwargs):
        state["calls"].append((command, kwargs))
        if command[0] == "git":
            if state["git_failure"]:
                return subprocess.CompletedProcess(command, 128, "", "test-secret-do-not-persist")
            assert not {"checkout", "reset", "switch", "clean", "pull"} & set(command)
            return REAL_RUN(command, **kwargs)
        if command[:2] == ["docker", "build"]:
            source = Path(command[-1])
            assert (source / "marker").read_text() == "committed bytes\n"
            assert not (source / "untracked").exists()
            assert f"VCS_REF={state['release']['source_commit']}" in command
            state["build_context"] = source
            return subprocess.CompletedProcess(command, 0, "built", "")
        if command[:3] == ["docker", "image", "inspect"]:
            info = {
                "Id": state["image_id"],
                "Config": {
                    "Labels": {
                        "org.opencontainers.image.revision": state["revision"],
                    }
                },
            }
            return subprocess.CompletedProcess(command, 0, json.dumps(info), "")
        if command[:2] == ["docker", "run"]:
            assert "--rm" in command and "--entrypoint" in command
            assert not {"-v", "--volume", "--mount", "-e", "--env"} & set(command)
            assert state["image_id"] in command
            assert kwargs["capture_output"] is True
            return subprocess.CompletedProcess(command, 0, json.dumps(state["payload"]), "")
        if command[0] == "./mindtrial":
            assert kwargs == {"cwd": state["mindtrial"], "check": False}
            return subprocess.CompletedProcess(command, state["live_status"])
        raise AssertionError(f"Unexpected subprocess: {command}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    return state


def manifests(state):
    return [
        json.loads(path.read_text())
        for path in sorted((state["package"] / "results").glob("*/manifest.json"))
    ]


def profile_setup(setup, profile):
    state = setup
    package = state["package"]
    for name in profile.configs:
        shutil.copyfile(ROOT / "examples/mindtrial" / name, package / name)
    tasks = {}
    for suite in profile.suites:
        name = f"nexus-{profile.name}-{suite}-tasks.yaml"
        shutil.copyfile(ROOT / "examples/mindtrial" / name, package / name)
        tasks[suite] = json.loads((package / name).read_text())
    shutil.copyfile(RUNNER, package / "pilot_runner.py")
    shutil.copyfile(ROOT / f"examples/mindtrial/{profile.name}-runner.py", package / "runner.py")
    release = state["release"]
    release["image"] = profile.image
    release["config_contract_sha256"] = {
        name: runner.config_contract_sha256(json.loads((package / name).read_text()))
        for name in profile.configs
    }
    release["files_sha256"] = {
        path.name: runner.sha256(path.read_bytes())
        for path in package.iterdir()
        if path.name != "release.json"
    }
    dump(package / "release.json", release)
    state["payload"] = {
        "runtime_source_sha256": RUNTIME,
        "reports": {profile.name: {"status": "passed"}},
        "tasks": tasks,
    }
    return state


@pytest.fixture
def interference_setup(setup):
    return profile_setup(setup, runner.INTERFERENCE)


@pytest.fixture
def comparison_setup(setup):
    return profile_setup(setup, runner.INTERFERENCE_COMPARISON)


@pytest.mark.parametrize("image_id", [IMAGE_ID, BARE_IMAGE_ID])
def test_comparison_preserves_both_model_runs_for_both_suites(comparison_setup, image_id):
    state = comparison_setup
    state["image_id"] = image_id
    profile = runner.INTERFERENCE_COMPARISON
    assert runner.main(["--suite", "all"], package_dir=state["package"], pilot=profile) == 0
    records = manifests(state)
    assert {record["suite"] for record in records} == {"core", "slack"}
    assert len(records) == 2
    for record in records:
        assert record["version"] == "interference-comparison-run-v1"
        assert record["evaluation_seed"] == "nexus-interference-comparison-pilot-v1"
        assert record["input_config_file"] == profile.configs[0]
        output = Path(record["output_dir"])
        effective = json.loads((output / "config.yaml").read_text())["config"]
        provider = effective["providers"][0]
        assert provider["name"] == "openai"
        assert provider["retry-policy"]["max-retry-attempts"] == 0
        assert [run["model"] for run in provider["runs"]] == ["gpt-6-astra", "gpt-6-luna"]
        assert all(
            run["disabled"] is False
            and run["max-requests-per-minute"] == 20
            and run["model-parameters"] == {"reasoning-effort": "medium"}
            for run in provider["runs"]
        )
        assert all(
            item["image"] == image_id
            for section in ("tools", "services", "validators")
            for item in effective[section]
        )
        assert len(json.loads((output / "tasks.yaml").read_text())["task-config"]["tasks"]) == 16
    (qualifier,) = [command for command, _ in state["calls"] if command[:2] == ["docker", "run"]]
    assert qualifier[-1] == profile.preflight_script
    assert (
        "from nexus.evaluation.interference_comparison import export_tasks, preflight"
        in qualifier[-1]
    )
    assert "--repeat" not in qualifier


def test_comparison_keeps_original_neutral_integration_and_task_limits():
    examples = ROOT / "examples/mindtrial"
    original = json.loads((examples / "nexus-interference-config.yaml").read_text())["config"]
    comparison = json.loads((examples / "nexus-interference-comparison-config.yaml").read_text())[
        "config"
    ]
    for section in ("tools", "services", "validators"):
        for item in comparison[section]:
            item["image"] = runner.INTERFERENCE.image
        assert comparison[section] == original[section]
    for suite in ("core", "slack"):
        original_tasks = json.loads(
            (examples / f"nexus-interference-{suite}-tasks.yaml").read_text()
        )
        compared_tasks = json.loads(
            (examples / f"nexus-interference-comparison-{suite}-tasks.yaml").read_text()
        )
        assert compared_tasks == original_tasks


@pytest.mark.parametrize("drift", ["disable", "remove", "append", "retry"])
def test_comparison_contract_rejects_run_set_or_retry_drift_before_build(comparison_setup, drift):
    profile = runner.INTERFERENCE_COMPARISON
    path = comparison_setup["package"] / profile.configs[0]
    config = json.loads(path.read_text())
    provider = config["config"]["providers"][0]
    if drift == "disable":
        provider["runs"][1]["disabled"] = True
    elif drift == "remove":
        provider["runs"].pop()
    elif drift == "append":
        provider["runs"].append(copy.deepcopy(provider["runs"][0]))
    else:
        provider["retry-policy"]["max-retry-attempts"] = 1
    dump(path, config)
    assert runner.main([], package_dir=comparison_setup["package"], pilot=profile) == 1
    assert comparison_setup["calls"] == []


@pytest.mark.parametrize("tamper", ["old-report", "failed-report", "tasks"])
def test_comparison_requires_its_structural_report_before_model_calls(comparison_setup, tamper):
    state = comparison_setup
    if tamper == "old-report":
        state["payload"]["reports"] = {"interference": {"status": "passed"}}
    elif tamper == "failed-report":
        state["payload"]["reports"]["interference-comparison"]["status"] = "blocked"
    else:
        state["payload"]["tasks"]["slack"]["task-config"]["tasks"].pop()
    assert (
        runner.main(
            ["--skip-build"], package_dir=state["package"], pilot=runner.INTERFERENCE_COMPARISON
        )
        == 1
    )
    assert not any(command[0] == "./mindtrial" for command, _ in state["calls"])


@pytest.mark.parametrize("image_id", [IMAGE_ID, BARE_IMAGE_ID])
def test_interference_profile_runs_both_paired_suites_with_immutable_images(
    interference_setup, image_id
):
    state = interference_setup
    state["image_id"] = image_id
    assert (
        runner.main(["--suite", "all"], package_dir=state["package"], pilot=runner.INTERFERENCE)
        == 0
    )
    records = manifests(state)
    assert len(records) == 2
    assert {r["suite"] for r in records} == {"core", "slack"}
    for record in records:
        assert record["version"] == "interference-run-v1"
        assert record["evaluation_seed"] == "nexus-interference-pilot-v1"
        assert record["input_config_file"] == "nexus-interference-config.yaml"
        output = Path(record["output_dir"])
        config = json.loads((output / "config.yaml").read_text())["config"]
        assert all(config[k][0]["image"] == image_id for k in ("tools", "services", "validators"))
        assert len(json.loads((output / "tasks.yaml").read_text())["task-config"]["tasks"]) == 16
    assert not any("--repeat" in command for command, _ in state["calls"])


@pytest.mark.parametrize("tamper", ["report", "tasks", "source"])
def test_interference_preflight_fails_closed_before_model_calls(interference_setup, tamper):
    state = interference_setup
    if tamper == "report":
        state["payload"]["reports"] = {"coordination": {"status": "passed"}}
    elif tamper == "tasks":
        state["payload"]["tasks"]["slack"]["task-config"]["tasks"].pop()
    else:
        state["payload"]["runtime_source_sha256"] = "d" * 64
    assert (
        runner.main(["--skip-build"], package_dir=state["package"], pilot=runner.INTERFERENCE) == 1
    )
    assert not any(command[0] == "./mindtrial" for command, _ in state["calls"])


@pytest.mark.parametrize("profile", ["interference", "interference-comparison"])
def test_interference_wrapper_exposes_only_its_suites(profile):
    result = REAL_RUN(
        [sys.executable, str(ROOT / f"examples/mindtrial/{profile}-runner.py"), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "{core,slack,all}" in result.stdout
    assert "spatial" not in result.stdout


@pytest.mark.parametrize("image_id", [IMAGE_ID, BARE_IMAGE_ID])
def test_default_paths_spaces_distinct_cwd_and_pinned_build_leave_checkout_untouched(
    setup, image_id
):
    state = setup
    state["image_id"] = image_id
    index = (state["repository"] / ".git/index").read_bytes()
    assert runner.main([], package_dir=state["package"]) == 0
    (record,) = manifests(state)
    output = Path(record["output_dir"])
    assert output.parent == state["package"] / "results"
    assert output.name.startswith("core-")
    assert record["cwd"] == str(state["home"] / "MindTrial")
    assert record["source_commit"] == state["release"]["source_commit"]
    assert record["status"] == "completed"
    assert record["input_config_file"] == runner.CONFIG
    assert (
        record["input_config_contract_sha256"]
        == state["release"]["config_contract_sha256"][runner.CONFIG]
    )
    assert record["image"] == {"tag": runner.IMAGE, "id": image_id, "revision": state["revision"]}
    assert record["mindtrial_sha256"] == runner.sha256(
        (state["mindtrial"] / "mindtrial").read_bytes()
    )
    assert record["command"] == [
        "./mindtrial",
        f"-config={output / 'config.yaml'}",
        f"-tasks={output / 'tasks.yaml'}",
        "--debug",
        "--interactive=true",
        "--json",
        "--evaluation-seed=nexus-coordination-pilot-v1",
        "run",
    ]
    effective = json.loads((output / "config.yaml").read_text())["config"]
    assert effective["output-dir"] == str(output)
    assert effective["log-file"] == str(output / "mindtrial.log")
    assert effective["task-source"] == str(output / "tasks.yaml")
    assert all(
        effective[key][0]["image"] == image_id for key in ("tools", "services", "validators")
    )
    assert (state["repository"] / "marker").read_text() == "uncommitted user work\n"
    assert (state["repository"] / "untracked").read_text() == "untracked user work\n"
    assert (state["repository"] / ".git/index").read_bytes() == index
    assert not state["build_context"].exists()
    assert not any("fetch" in command for command, _ in state["calls"])


def test_preflight_only_needs_neither_api_key_nor_mindtrial_and_never_launches_it(
    setup, monkeypatch
):
    monkeypatch.delenv("OPENAI_API_KEY")
    shutil.rmtree(setup["mindtrial"])
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 0
    (record,) = manifests(setup)
    assert record["status"] == "preflight-passed" and record["command"] is None
    assert not any(command[0] == "./mindtrial" for command, _ in setup["calls"])


@pytest.mark.parametrize("failure", ["revision", "digest", "tasks", "report"])
@pytest.mark.parametrize("image_id", [IMAGE_ID, BARE_IMAGE_ID])
def test_skip_build_still_blocks_wrong_image_or_stale_qualification(setup, failure, image_id):
    setup["image_id"] = image_id
    if failure == "revision":
        setup["revision"] = "0" * 40
    elif failure == "digest":
        setup["payload"]["runtime_source_sha256"] = "0" * 64
    elif failure == "tasks":
        setup["payload"]["tasks"]["spatial"]["task-config"]["tasks"][0]["name"] = "stale"
    else:
        setup["payload"]["reports"]["coordination"]["status"] = "blocked"
    assert runner.main(["--skip-build"], package_dir=setup["package"]) == 1
    assert any(command[:3] == ["docker", "image", "inspect"] for command, _ in setup["calls"])
    assert not any(command[0] in ("git", "./mindtrial") for command, _ in setup["calls"])
    assert not (setup["package"] / "results").exists()


@pytest.mark.parametrize(
    "image_id",
    [
        "",
        "nexus:coordination-v1",
        "b" * 12,
        "b" * 63,
        "b" * 65,
        "g" * 64,
        "sha256:" + "b" * 63,
        "sha512:" + "b" * 64,
        None,
        1,
        int("1" * 64),
    ],
)
def test_malformed_image_id_blocks_before_qualification_or_model_run(setup, image_id, capsys):
    setup["image_id"] = image_id
    assert runner.main(["--skip-build"], package_dir=setup["package"]) == 1
    assert "invalid image ID" in capsys.readouterr().err
    assert not any(
        command[:2] == ["docker", "run"] or command[0] == "./mindtrial"
        for command, _ in setup["calls"]
    )


@pytest.mark.parametrize(
    "suite, filename", [("core", runner.CONFIG), ("repeat", runner.REPEAT_CONFIG)]
)
def test_edited_model_and_effort_preserved_and_recorded_without_credentials(
    setup, capsys, suite, filename
):
    path = setup["package"] / filename
    edited = json.loads(path.read_text())
    run = edited["config"]["providers"][0]["runs"][0]
    run.update(
        model="a-different-model",
        name="My chosen model",
        **{"model-parameters": {"reasoning-effort": "low"}, "max-requests-per-minute": 10},
    )
    dump(path, edited)
    assert runner.main(["--skip-build", "--suite", suite], package_dir=setup["package"]) == 0
    (record,) = manifests(setup)
    assert record["input_config_matches_release"] is False
    assert record["input_config_sha256"] == runner.sha256(path.read_bytes())
    assert record["input_config_file"] == filename
    assert (
        record["input_config_contract_sha256"]
        == setup["release"]["config_contract_sha256"][filename]
    )
    output = Path(record["output_dir"])
    effective = json.loads((output / "config.yaml").read_text())
    assert effective["config"]["providers"] == edited["config"]["providers"]
    assert (output / "input-config.yaml").read_bytes() == path.read_bytes()
    secret = os.environ["OPENAI_API_KEY"]
    for artifact in output.iterdir():
        assert secret.encode() not in artifact.read_bytes()
    captured = capsys.readouterr()
    assert secret not in captured.out + captured.err


@pytest.mark.parametrize(
    "suite, filename", [("core", runner.CONFIG), ("repeat", runner.REPEAT_CONFIG)]
)
@pytest.mark.parametrize(
    "drift",
    [
        "input-env",
        "providers-empty",
        "provider-name",
        "retries",
        "tool-schema",
        "tool-name",
        "run-disabled",
        "extra-run",
        "task-retries",
    ],
)
def test_config_contract_blocks_integration_provider_and_retry_drift(setup, suite, filename, drift):
    path = setup["package"] / filename
    document = json.loads(path.read_text())
    config = document["config"]
    if drift == "input-env":
        del config["services"][0]["input-env"]["ontology-options"]
    elif drift == "providers-empty":
        config["providers"] = []
    elif drift == "provider-name":
        config["providers"][0]["name"] = "different-provider"
    elif drift == "retries":
        config["providers"][0]["retry-policy"]["max-retry-attempts"] = 5
    elif drift == "tool-schema":
        config["tools"][0]["parameters"]["required"] = []
    elif drift == "tool-name":
        config["tools"][0]["name"] = "renamed-tool"
    elif drift == "run-disabled":
        config["providers"][0]["runs"][0]["disabled"] = True
    elif drift == "extra-run":
        config["providers"][0]["runs"].append(copy.deepcopy(config["providers"][0]["runs"][0]))
    elif drift == "task-retries":
        config["retry-policy"] = {"max-retry-attempts": 5}
    dump(path, document)
    assert runner.main(["--suite", suite], package_dir=setup["package"]) == 1
    assert setup["calls"] == []
    assert not (setup["package"] / "results").exists()


def test_repeat_preserves_historical_interface_with_current_default_provider_settings():
    folder = ROOT / "examples/mindtrial"
    historical = json.loads((folder / "nexus-planning-resource-config.yaml").read_text())
    coordination = json.loads((folder / runner.CONFIG).read_text())
    repeat = json.loads((folder / runner.REPEAT_CONFIG).read_text())
    expected = copy.deepcopy(historical)
    expected["config"]["providers"] = coordination["config"]["providers"]
    expected["config"]["task-source"] = "./nexus-coordination-repeat-tasks.yaml"
    for section in ("tools", "services", "validators"):
        for entry in expected["config"][section]:
            entry["image"] = runner.IMAGE
    assert repeat == expected
    assert (
        repeat["config"]["tools"][0]["description"]
        != coordination["config"]["tools"][0]["description"]
    )


def test_all_uses_each_configs_independent_model_choices_and_repeat_interface(setup):
    for name, model in (
        (runner.CONFIG, "coordination-model"),
        (runner.REPEAT_CONFIG, "repeat-model"),
    ):
        path = setup["package"] / name
        document = json.loads(path.read_text())
        document["config"]["providers"][0]["runs"][0]["model"] = model
        dump(path, document)
    assert runner.main(["--skip-build", "--suite", "all"], package_dir=setup["package"]) == 0
    for record in manifests(setup):
        filename = runner.REPEAT_CONFIG if record["suite"] == "repeat" else runner.CONFIG
        original = json.loads((setup["package"] / filename).read_text())["config"]
        effective = json.loads((Path(record["output_dir"]) / "config.yaml").read_text())["config"]
        assert record["input_config_file"] == filename
        assert effective["providers"] == original["providers"]
        assert effective["tools"][0]["description"] == original["tools"][0]["description"]


def test_all_validates_repeat_config_before_starting_any_suite(setup):
    path = setup["package"] / runner.REPEAT_CONFIG
    document = json.loads(path.read_text())
    document["config"]["providers"] = []
    dump(path, document)
    assert runner.main(["--suite", "all"], package_dir=setup["package"]) == 1
    assert setup["calls"] == []


@pytest.mark.parametrize("field", ["files_sha256", "config_contract_sha256"])
def test_release_requires_second_config_byte_and_contract_hash(setup, field):
    del setup["release"][field][runner.REPEAT_CONFIG]
    dump(setup["package"] / "release.json", setup["release"])
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 1
    assert setup["calls"] == []


def test_embedded_api_key_rejected_before_build_and_never_persisted_or_printed(setup, capsys):
    path = setup["package"] / runner.CONFIG
    config = json.loads(path.read_text())
    config["config"]["providers"][0]["client-config"]["api-key"] = "embedded-secret"
    dump(path, config)
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 1
    assert setup["calls"] == []
    assert not (setup["package"] / "results").exists()
    captured = capsys.readouterr()
    assert "embedded-secret" not in captured.out + captured.err


def test_failure_status_and_exact_command_survive_and_all_stops_without_extra_paid_calls(setup):
    setup["live_status"] = 7
    assert runner.main(["--skip-build", "--suite", "all"], package_dir=setup["package"]) == 7
    (record,) = manifests(setup)
    assert record["status"] == "failed" and record["exit_code"] == 7
    assert record["finished_at"] >= record["started_at"]
    assert sum(command[0] == "./mindtrial" for command, _ in setup["calls"]) == 1


def test_all_runs_sequentially_with_separate_outputs_and_historical_repeat_seed(setup):
    assert runner.main(["--skip-build", "--suite", "all"], package_dir=setup["package"]) == 0
    records = manifests(setup)
    assert {record["suite"] for record in records} == set(runner.SUITES)
    assert len({record["output_dir"] for record in records}) == 4
    seeds = {record["suite"]: record["evaluation_seed"] for record in records}
    assert seeds == {
        "core": "nexus-coordination-pilot-v1",
        "slack": "nexus-coordination-pilot-v1",
        "spatial": "nexus-coordination-pilot-v1",
        "repeat": "nexus-pr-pilot-v1",
    }
    commands = [command for command, _ in setup["calls"] if command[0] == "./mindtrial"]
    assert [
        Path(command[1].removeprefix("-config=")).parent.name.split("-")[0] for command in commands
    ] == list(runner.SUITES)
    (qualify,) = [command for command, _ in setup["calls"] if command[:2] == ["docker", "run"]]
    assert qualify[-1] == "--repeat"


def test_read_only_checkout_is_archived_without_writing_or_changing_head(setup):
    repository = setup["repository"]
    (repository / "marker").chmod(0o444)
    repository.chmod(0o555)
    try:
        assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 0
        assert (repository / "marker").read_text() == "uncommitted user work\n"
        assert (repository / "marker").stat().st_mode & 0o777 == 0o444
    finally:
        repository.chmod(0o755)
        (repository / "marker").chmod(0o644)


def test_local_git_errors_block_without_fetch_build_or_leaking_stderr(setup, capsys):
    setup["git_failure"] = True
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 1
    assert len(setup["calls"]) == 1
    captured = capsys.readouterr()
    assert os.environ["OPENAI_API_KEY"] not in captured.out + captured.err


def test_missing_commit_fetches_only_release_branch_without_checkout(setup, tmp_path):
    remote = tmp_path / "origin repository"
    REAL_RUN(
        ["git", "clone", str(setup["repository"]), str(remote)], check=True, capture_output=True
    )
    for arguments in (
        ["config", "user.email", "test@example.invalid"],
        ["config", "user.name", "Test"],
    ):
        REAL_RUN(["git", "-C", str(remote), *arguments], check=True, capture_output=True)
    (remote / "new-file").write_text("new release\n")
    for arguments in (["add", "."], ["commit", "-m", "new release"]):
        REAL_RUN(["git", "-C", str(remote), *arguments], check=True, capture_output=True)
    commit = REAL_RUN(
        ["git", "-C", str(remote), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    REAL_RUN(
        ["git", "-C", str(setup["repository"]), "remote", "add", "origin", str(remote)],
        check=True,
        capture_output=True,
    )
    setup["release"]["source_commit"] = commit
    setup["revision"] = commit
    dump(setup["package"] / "release.json", setup["release"])
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 0
    (fetch,) = [command for command, _ in setup["calls"] if "fetch" in command]
    assert fetch == [
        "git",
        "-C",
        str(setup["repository"]),
        "fetch",
        "--no-tags",
        "origin",
        runner.BRANCH,
    ]
    assert (setup["repository"] / "marker").read_text() == "uncommitted user work\n"


def test_release_task_tampering_blocked_before_subprocesses(setup):
    (setup["package"] / "nexus-coordination-core-tasks.yaml").write_text("{}")
    assert runner.main(["--preflight-only"], package_dir=setup["package"]) == 1
    assert setup["calls"] == []


def test_environment_overrides_and_repeated_invocations_create_unique_local_results(
    setup, monkeypatch
):
    repository = setup["home"] / "alternative NEXUS clone"
    mindtrial = setup["home"] / "alternative MindTrial"
    setup["repository"].rename(repository)
    setup["mindtrial"].rename(mindtrial)
    setup.update(repository=repository, mindtrial=mindtrial)
    monkeypatch.setenv("NEXUS_REPO", str(repository))
    monkeypatch.setenv("MINDTRIAL_DIR", str(mindtrial))
    binary_bytes = (mindtrial / "mindtrial").read_bytes()
    assert runner.main([], package_dir=setup["package"]) == 0
    assert runner.main(["--skip-build"], package_dir=setup["package"]) == 0
    records = manifests(setup)
    assert len({record["output_dir"] for record in records}) == 2
    assert all(record["cwd"] == str(mindtrial) for record in records)
    assert (mindtrial / "mindtrial").read_bytes() == binary_bytes


def test_repeat_exports_are_compared_after_planning_preflight(setup):
    setup["payload"]["tasks"]["repeat"]["task-config"]["tasks"][0]["name"] = "stale repeat"
    assert runner.main(["--skip-build", "--suite", "repeat"], package_dir=setup["package"]) == 1
    assert not any(command[0] == "./mindtrial" for command, _ in setup["calls"])
    (qualify,) = [command for command, _ in setup["calls"] if command[:2] == ["docker", "run"]]
    assert qualify[-1] == "--repeat"


@pytest.mark.parametrize("packaged", [True, False])
@pytest.mark.parametrize("profile", ["coordination", "interference", "interference-comparison"])
def test_bash_entrypoint_self_locates_and_preserves_arguments(tmp_path, packaged, profile):
    package = tmp_path / "package with spaces"
    package.mkdir()
    script = package / ("run.sh" if packaged else f"{profile}-run.sh")
    shutil.copyfile(ROOT / f"examples/mindtrial/{profile}-run.sh", script)
    helper = package / ("runner.py" if packaged else f"{profile}-runner.py")
    helper.write_text("import json, sys\nprint(json.dumps(sys.argv))\n")
    completed = REAL_RUN(
        ["bash", str(script), "--suite", "spatial", "argument with spaces"],
        cwd=tmp_path,
        env={**os.environ, "PYTHON": sys.executable},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(completed.stdout) == [
        str(helper),
        "--suite",
        "spatial",
        "argument with spaces",
    ]


@pytest.fixture
def comparison_package_setup(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "package_coordination", ROOT / "scripts/package_coordination.py"
    )
    assert spec is not None and spec.loader is not None
    packager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packager)
    source = tmp_path / "source"
    examples = source / "examples/mindtrial"
    examples.mkdir(parents=True)
    profile = runner.INTERFERENCE_COMPARISON
    source_names = {
        "coordination-runner.py",
        "interference-comparison-runner.py",
        "interference-comparison-run.sh",
        "interference-comparison-run.md",
        "summarize-pilot-results.py",
        *profile.configs,
        *(f"nexus-{profile.name}-{suite}-tasks.yaml" for suite in profile.suites),
    }
    for name in source_names:
        shutil.copyfile(ROOT / "examples/mindtrial" / name, examples / name)
    reports = source / "docs/research"
    reports.mkdir(parents=True)
    report_names = {
        "interference-comparison-preflight-2026-10-27.json",
        "ternary-feasibility-2026-10-27.json",
        "interference-comparison-validation-2026-10-27.md",
    }
    for name in report_names:
        (reports / name).write_text(f"fixture for {name}\n")
    shutil.copyfile(
        ROOT / "docs/interference-matrix.json", source / "docs/interference-matrix.json"
    )
    source_file = source / "src/nexus/fixture.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text('"""Isolated Python source fixture."""\n')
    sources = {"fixture.py": runner.sha256(source_file.read_bytes())}
    matrix = json.loads((source / "docs/interference-matrix.json").read_text())
    checks = {
        name: True
        for name in (
            "compiled_contract",
            "public_policy_supported_win",
            "exact_reference_actions",
            "exact_replay",
            "independent_optimum",
            "independent_restricted_baseline",
            "independent_coordinate_break_minimum",
            "paired_seed_kernel_and_target",
            "complete_transition_checks",
            "tool_limit_covers_allowance",
            "horizon_stratum_bound",
            "factorization_or_optimal_interleaving",
            "coupled_coordinate_regression_required",
        )
    }
    structural_checks = {
        name: True
        for name in (
            "independent_structural_costs",
            "coordinate_metric_matches_original",
            "block_cost_ordering",
            "live_structural_diagnostics",
        )
    }
    preflight = {
        "version": "interference-comparison-preflight-v1",
        "status": "passed",
        "sources": sources,
        "matrix_sha256": runner.sha256(
            json.dumps(matrix, sort_keys=True, separators=(",", ":")).encode()
        ),
        "cells": [
            {**row, "checks": checks, "structural_checks": structural_checks}
            for row in matrix["runs"]
        ],
    }
    feasibility = {
        "version": "ternary-feasibility-v1",
        "status": "completed",
        "sources": sources,
        "seeds": [67, 79, 101, 103],
        "kernel_attempt_limit_per_seed": 32,
        "state_bound": 19683,
        "variants": ["spill-ring", "boundary-crossguard", "all-crossguard", "self-guard"],
        "first_admission_gate": {"minimum_machine_blocks": 16},
        "second_admission_gate": {"minimum_whole_bank_reopening_operations": 2},
        "live_tasks_exported": 0,
        "first_gate_candidate_count": 1,
        "second_gate_candidate_count": 0,
        "admission": "no-target-passes-tested-gates",
        "kernels": [
            {
                "seed": seed,
                "attempt": attempt,
                "variant": variant,
                "independent_transition_checks": 177147,
                "coupled_transition_checks": 177147,
                "independent_block_oracle_agrees": True,
                "targets_passing_first_gate": [],
                "candidate_proofs": [],
            }
            for seed in (67, 79, 101, 103)
            for attempt in range(1, 33)
            for variant in ("spill-ring", "boundary-crossguard", "all-crossguard", "self-guard")
        ],
    }
    feasibility["kernels"][0].update(
        targets_passing_first_gate=[9841],
        candidate_proofs=[
            {
                "target": [1] * 9,
                "state": 9841,
                "minimum_operations": 17,
                "minimum_machine_blocks": 16,
                "minimum_whole_bank_reopening_operations": 1,
                "second_gate_passed": False,
            }
        ],
    )
    dump(reports / "interference-comparison-preflight-2026-10-27.json", preflight)
    dump(reports / "ternary-feasibility-2026-10-27.json", feasibility)
    (source / "docs/interference-comparison-guide.md").write_text("Comparison guide fixture\n")
    monkeypatch.setattr(packager, "ROOT", source)
    commit = "a" * 40

    def git_output(command, **kwargs):
        assert command[:3] == ["git", "-C", str(source)]
        assert kwargs == {"text": True}
        if command[3:] == ["status", "--porcelain"]:
            return ""
        assert command[3:] == ["rev-parse", "HEAD"]
        return commit + "\n"

    monkeypatch.setattr(packager.subprocess, "check_output", git_output)
    destination = tmp_path / "comparison package"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "package_interference_comparison.py",
            "--output-dir",
            str(destination),
            "--runtime-source-sha256",
            RUNTIME,
        ],
    )
    return {
        "packager": packager,
        "source": source,
        "destination": destination,
        "report_names": report_names,
        "profile": profile,
        "commit": commit,
    }


def test_comparison_package_binds_launcher_config_guide_and_qualification_reports(
    comparison_package_setup,
):
    state = comparison_package_setup
    packager, destination = state["packager"], state["destination"]
    profile, commit, report_names = state["profile"], state["commit"], state["report_names"]
    packager.main(pilot_name=profile.name)
    release = runner.load_release(destination, profile)
    assert release["source_commit"] == commit
    assert release["image"] == profile.image
    assert release["runtime_source_sha256"] == RUNTIME
    assert release["design_url"].endswith(f"/{commit}/docs/interference-comparison-guide.md")
    assert set(release["files_sha256"]) == {
        "run.sh",
        "runner.py",
        "pilot_runner.py",
        "README.md",
        "guide.md",
        "summarize_results.py",
        *profile.configs,
        *(f"nexus-{profile.name}-{suite}-tasks.yaml" for suite in profile.suites),
        *(f"reports/{name}" for name in report_names),
    }
    config, _ = runner.load_config(destination, release, profile.configs[0])
    assert len(config["config"]["providers"][0]["runs"]) == 2
    with zipfile.ZipFile(destination.with_suffix(".zip")) as archive:
        assert f"{destination.name}/guide.md" in archive.namelist()
        assert f"{destination.name}/pilot_runner.py" in archive.namelist()
        assert f"{destination.name}/summarize_results.py" in archive.namelist()
    (destination / "guide.md").write_text("changed operator guidance\n")
    with pytest.raises(runner.RunnerError, match="Release checksum mismatch: guide.md"):
        runner.load_release(destination, profile)


@pytest.mark.parametrize("report", ["interference-comparison-preflight", "ternary-feasibility"])
@pytest.mark.parametrize("failure", ["empty", "running", "stale", "partial", "duplicate"])
def test_comparison_package_rejects_incomplete_or_stale_reports_before_copy(
    comparison_package_setup, report, failure
):
    state = comparison_package_setup
    path = state["source"] / f"docs/research/{report}-2026-10-27.json"
    document = json.loads(path.read_text())
    if failure == "empty":
        document = {}
    elif failure == "running":
        document["status"] = "running"
    elif failure == "stale":
        document["sources"]["fixture.py"] = "d" * 64
    else:
        records = document["cells" if report == "interference-comparison-preflight" else "kernels"]
        if failure == "partial":
            records.pop()
        else:
            records[-1] = copy.deepcopy(records[0])
    dump(path, document)
    with pytest.raises(SystemExit) as blocked:
        state["packager"].main(pilot_name="interference-comparison")
    assert blocked.value.code == 2
    assert not state["destination"].exists()


@pytest.mark.parametrize("field", ["checks", "structural_checks"])
@pytest.mark.parametrize("failure", ["missing", "false", "truthy-integer"])
def test_comparison_package_requires_every_named_preflight_check(
    comparison_package_setup, field, failure
):
    state = comparison_package_setup
    path = state["source"] / "docs/research/interference-comparison-preflight-2026-10-27.json"
    document = json.loads(path.read_text())
    checks = document["cells"][0][field]
    name = next(iter(checks))
    if failure == "missing":
        del checks[name]
    else:
        checks[name] = False if failure == "false" else 1
    dump(path, document)
    with pytest.raises(ValueError, match="missing or failed"):
        state["packager"].validate_comparison_reports(state["source"])


@pytest.mark.parametrize("failure", ["source-changed", "source-added", "matrix-changed"])
def test_comparison_package_binds_reports_to_current_source_and_matrix(
    comparison_package_setup, failure
):
    state = comparison_package_setup
    if failure == "source-changed":
        (state["source"] / "src/nexus/fixture.py").write_text("changed = True\n")
    elif failure == "source-added":
        (state["source"] / "src/nexus/added.py").write_text("added = True\n")
    else:
        path = state["source"] / "docs/interference-matrix.json"
        document = json.loads(path.read_text())
        document["runs"][0]["seed"] = 999
        dump(path, document)
    with pytest.raises(ValueError, match="source map is stale|matrix digest differs"):
        state["packager"].validate_comparison_reports(state["source"])


@pytest.mark.parametrize(
    "failure",
    [
        "seeds",
        "variants",
        "attempt-limit",
        "state-bound",
        "first-gate",
        "second-gate",
        "live-tasks",
        "pending-kernel",
        "independent-transitions",
        "coupled-transitions",
        "block-oracle",
        "missing-proof",
        "pending-proof",
        "wrong-proof-state",
        "wrong-second-gate-result",
        "first-total",
        "second-total",
        "admission",
        "passed-gates",
    ],
)
def test_comparison_package_rejects_inconsistent_feasibility_proofs(
    comparison_package_setup, failure
):
    state = comparison_package_setup
    path = state["source"] / "docs/research/ternary-feasibility-2026-10-27.json"
    document = json.loads(path.read_text())
    kernel = document["kernels"][0]
    proof = kernel["candidate_proofs"][0]
    mutations = {
        "seeds": lambda: document["seeds"].pop(),
        "variants": lambda: document["variants"].pop(),
        "attempt-limit": lambda: document.update(kernel_attempt_limit_per_seed=31),
        "state-bound": lambda: document.update(state_bound=19682),
        "first-gate": lambda: document["first_admission_gate"].update(minimum_machine_blocks=15),
        "second-gate": lambda: document["second_admission_gate"].update(
            minimum_whole_bank_reopening_operations=1
        ),
        "live-tasks": lambda: document.update(live_tasks_exported=1),
        "pending-kernel": lambda: kernel.update(status="running"),
        "independent-transitions": lambda: kernel.update(independent_transition_checks=177146),
        "coupled-transitions": lambda: kernel.update(coupled_transition_checks=177146),
        "block-oracle": lambda: kernel.update(independent_block_oracle_agrees=False),
        "missing-proof": lambda: kernel["candidate_proofs"].clear(),
        "pending-proof": lambda: proof.update(status="running"),
        "wrong-proof-state": lambda: proof.update(state=9842),
        "wrong-second-gate-result": lambda: proof.update(second_gate_passed=True),
        "first-total": lambda: document.update(first_gate_candidate_count=0),
        "second-total": lambda: document.update(second_gate_candidate_count=1),
        "admission": lambda: document.update(admission="admitted"),
    }
    if failure == "passed-gates":
        proof.update(minimum_whole_bank_reopening_operations=2, second_gate_passed=True)
        document.update(
            second_gate_candidate_count=1, admission="later-gates-required-no-admission"
        )
    else:
        mutations[failure]()
    dump(path, document)
    with pytest.raises(ValueError, match="comparison reports:"):
        state["packager"].validate_comparison_reports(state["source"])
