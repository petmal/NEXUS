"""Export five provider configs and an unchanged subset of qualified source tasks.

Full mechanical qualification remains the shared package/launcher gate. This
exporter never calls a provider and never edits historical exports.
"""

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/mindtrial"


def export():
    spec = importlib.util.spec_from_file_location(
        "pilot_runner", EXAMPLES / "coordination-runner.py"
    )
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    matrix = json.loads((ROOT / "docs/capability-smoke-matrix.json").read_text())
    if matrix["selection"] != json.loads(json.dumps(runner.CAPABILITY_SELECTION)):
        raise ValueError("Matrix selection differs from the container selector")
    if [m["id"] for m in matrix["models"]] != list(runner.CAPABILITY_MODELS):
        raise ValueError("Model IDs differ from the launcher")
    exports = {
        suite: json.loads((EXAMPLES / f"nexus-cross-axis-{suite}-tasks.yaml").read_text())
        for suite in runner.CROSS_AXIS.suites
    }
    files = {
        f"nexus-capability-smoke-{suite}-tasks.yaml": value
        for suite, value in runner.select_capability_tasks(exports).items()
    }
    base = json.loads((EXAMPLES / "nexus-cross-axis-smoke-config.yaml").read_text())
    for model in matrix["models"]:
        config = copy.deepcopy(base)
        settings = config["config"]
        settings["task-source"] = "./nexus-capability-smoke-controls-tasks.yaml"
        settings["providers"] = [
            {
                "name": model["provider"],
                "retry-policy": {"max-retry-attempts": 0, "initial-delay-seconds": 30},
                "client-config": {"api-key": ""},
                "runs": [
                    {
                        "name": model["name"],
                        "disabled": False,
                        "model": model["model"],
                        "max-requests-per-minute": model["max-requests-per-minute"],
                        "model-parameters": model["model-parameters"],
                    }
                ],
            }
        ]
        for section in ("tools", "services", "validators"):
            for item in settings[section]:
                item["image"] = runner.CAPABILITY_SMOKE.image
        files[f"nexus-capability-smoke-{model['id']}-config.yaml"] = config
    return files


if __name__ == "__main__":
    for name, value in export().items():
        (EXAMPLES / name).write_text(json.dumps(value, indent=2) + "\n")
