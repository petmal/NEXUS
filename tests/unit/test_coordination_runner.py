"""Exercise the launcher at real subprocess boundaries; never call a live model."""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
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
def test_bash_entrypoint_self_locates_and_preserves_arguments(tmp_path, packaged):
    package = tmp_path / "package with spaces"
    package.mkdir()
    script = package / ("run.sh" if packaged else "coordination-run.sh")
    shutil.copyfile(LAUNCHER, script)
    helper = package / ("runner.py" if packaged else "coordination-runner.py")
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
