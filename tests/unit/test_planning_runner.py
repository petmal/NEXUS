"""The downloadable runner must select the qualified worlds and live validator."""

import json
from pathlib import Path

from nexus.evaluation.planning import Pilot

ROOT = Path(__file__).parents[2]


def test_mindtrial_runner_wires_every_qualified_cell_to_one_persistent_service():
    directory = ROOT / "examples/mindtrial"
    config = json.loads((directory / "nexus-planning-resource-config.yaml").read_text())["config"]
    tasks = json.loads((directory / config["task-source"]).read_text())["task-config"]
    pilot = Pilot.model_validate_json((ROOT / "docs/planning-resource-matrix.json").read_text())
    assert len(config["tools"]) == len(config["services"]) == len(config["validators"]) == 1
    tool, service, validator = (config[key][0] for key in ("tools", "services", "validators"))
    assert {tool["image"], service["image"], validator["image"]} == {"nexus:planning-resource-v1"}
    assert service["command"] == ["serve-session"]
    assert service["healthcheck"] == ["nexus", "health"]
    for consumer in (tool, validator):
        assert consumer["dependencies"] == [
            {"service": "nexus", "env": {"NEXUS_URL": "{{ .Endpoint }}"}}
        ]
    assert tool["command"] == ["request", "--request-file", tool["parameter-files"]["request"]]
    assert validator["command"] == [
        "validate",
        "--candidate-file",
        validator["template-files"][0]["path"],
    ]
    assert validator["template-files"][0]["template"] == "{{ .Candidate.Response }}"
    assert tasks["validation-rules"]["custom-validator"] == validator["name"]
    assert tasks["max-turns"] == pilot.max_turns
    assert tasks["tool-selector"]["tools"][0]["max-calls"] == pilot.recommended_tool_call_limit
    assert len(tasks["tasks"]) == len(pilot.runs)
    for task, cell in zip(tasks["tasks"], pilot.runs, strict=True):
        assert task["disabled"] is False
        inputs = task["tool-selector"]["service-inputs"]["nexus"]
        assert inputs["science-family"] == pilot.family
        assert inputs["seed"] == str(cell.seed)
        assert (
            inputs["theory-level"],
            inputs["discovery-level"],
            inputs["planning-level"],
            inputs["resource-pressure"],
        ) == (cell.theory, cell.discovery, cell.planning, cell.resource)
        assert inputs.keys() <= service["input-env"].keys()
        assert inputs["extended-diagnostics"] is True
    assert not tool.get("shared-dir") and not tool.get("env")
    actions = tool["parameters"]["properties"]["request"]["properties"]["action"]["properties"]
    assert set(actions["type"]["enum"]) == {
        "observe",
        "move",
        "take",
        "drop",
        "operate",
        "probe",
        "wait",
        "finish",
    }
    assert "settings" not in actions


def test_runner_enables_one_inherited_model_without_secret_or_hidden_task_retries():
    config = json.loads(
        (ROOT / "examples/mindtrial/nexus-planning-resource-config.yaml").read_text()
    )["config"]
    assert len(config["providers"]) == 1
    provider = config["providers"][0]
    assert provider["name"] == "openai"
    assert provider["client-config"]["api-key"] == ""
    assert provider["retry-policy"]["max-retry-attempts"] == 0
    assert len(provider["runs"]) == 1
    run = provider["runs"][0]
    assert not run["disabled"] and run["model"] == "gpt-6-astra"
    assert run["model-parameters"] == {"reasoning-effort": "medium"}
    assert "pricing" not in run  # No stale tariff is presented as a current price.
