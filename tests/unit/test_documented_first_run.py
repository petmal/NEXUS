"""The tutorial must work without private hints, credentials or a paid model call."""

import json
import re
import runpy
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexus.cli import app

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/mindtrial"


def test_documented_demo_actions_reach_the_advertised_ending():
    guide = (ROOT / "docs/play-guide.md").read_text()
    snippet = re.search(r"^```jsonl\n(.*?)^```", guide, flags=re.M | re.S).group(1)
    result = CliRunner().invoke(app, ["demo", "--play"], input=snippet)
    assert result.exit_code == 0, result.stdout
    assert "turn 9 · won" in result.stdout and "Actions left: 10" in result.stdout
    assert "Victory receipt: NX-" in result.stdout


@pytest.mark.parametrize("provider,model,text", [
    ("openai", "example-model", False), ("openrouter", "vendor/example-model", True),
])
def test_first_model_tutorial_preserves_control_and_validator(tmp_path, provider, model, text):
    prepare = runpy.run_path(str(EXAMPLE / "first_run.py"))["prepare"]
    dest = tmp_path / "first"
    prepare(dest, provider, model, text)
    cfg = json.loads((dest / "config.yaml").read_text())["config"]
    taskset = json.loads((dest / "tasks.yaml").read_text())["task-config"]
    template = json.loads((EXAMPLE / "nexus-fresh-world-luna-config.yaml").read_text())["config"]
    full = json.loads((EXAMPLE / "nexus-fresh-world-controls-tasks.yaml").read_text())["task-config"]
    assert taskset["tasks"] == [t for t in full["tasks"] if t["name"] == "NEXUS fresh-F05"]
    assert len(taskset["tasks"]) == 1
    provider_config, = cfg["providers"]
    run, = provider_config["runs"]
    assert provider_config["name"] == provider and run["model"] == model
    assert provider_config["client-config"]["api-key"] == ""
    assert run["disable-structured-output"] is text and "model-parameters" not in run
    assert taskset["validation-rules"] == full["validation-rules"]
    for group in ("tools", "validators"):
        assert cfg[group] == [dict(item, image="nexus:first-run") for item in template[group]]
    service, = cfg["services"]
    assert service["bind-mounts"] == [{"source": "./private-audits", "target": "/nexus-audits", "writable": True}]
    assert service["input-env"] == {**template["services"][0]["input-env"], "audit-dir": "NEXUS_AUDIT_DIR"}
    assert taskset["tool-selector"]["service-inputs"]["nexus"] == {
        "audit-dir": "/nexus-audits/{{ .Service.InstanceID }}"
    }
    assert (dest / "private-audits").stat().st_mode & 0o777 == 0o700
    assert (dest / cfg["task-source"]).resolve() == dest / "tasks.yaml"
    assert taskset["max-turns"] == 40 and taskset["tool-selector"]["tools"][0]["max-calls"] == 32
    with pytest.raises(FileExistsError):
        prepare(dest, "other", "other", text)


def test_mount_smoke_links_every_attempt_to_the_result_trace():
    linked = runpy.run_path(str(EXAMPLE / "verify_mount_smoke.py"))["linked_attempts"]
    row = {"Task": "NEXUS fresh-F05", "TraceID": "trace"}
    results = {"Results": {"openai": [row]}}
    names = ["mindtrial-service-one", "mindtrial-service-two"]
    log = "\n".join(f'[trace] model: service nexus: created service container "{n}"' for n in names)
    assert linked(results, log, reversed(names)) == (row, names)
    for wrong_log, folders in [(log, names[:1]), (log.replace("[trace]", "[other]"), names),
                               (log, [*names, "unrelated"]), (log + "\n" + log, names)]:
        with pytest.raises(ValueError, match="instances"):
            linked(results, wrong_log, folders)
