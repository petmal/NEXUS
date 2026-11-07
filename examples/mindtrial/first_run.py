"""Prepare a one-model, one-control tutorial from the maintained MindTrial definitions."""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "nexus:first-run"


def prepare(directory, provider, model, text_output=False):
    config = json.loads((HERE / "nexus-fresh-world-luna-config.yaml").read_text())
    tasks = json.loads((HERE / "nexus-fresh-world-controls-tasks.yaml").read_text())
    settings = config["config"]
    # Use the known tool/service/validator contract; do not inherit Luna's inference settings.
    (backend,) = settings["providers"]
    backend["name"] = provider
    backend["runs"] = [{"name": model, "model": model, "disabled": False,
                        "max-requests-per-minute": 10, "disable-structured-output": text_output}]
    for group in ("tools", "services", "validators"):
        for entry in settings[group]:
            entry["image"] = IMAGE
    settings["task-source"] = "./tasks.yaml"
    taskset = tasks["task-config"]
    (control,) = (row for row in taskset["tasks"] if row["name"] == "NEXUS fresh-F05")
    taskset["tasks"] = [control]
    # Tutorial limits are separate from the published panel and the world's action budget.
    taskset["max-turns"] = 40
    taskset["tool-selector"]["tools"][0]["max-calls"] = 32
    directory.mkdir(parents=True, exist_ok=False)
    for name, data in (("config.yaml", config), ("tasks.yaml", tasks)):
        (directory / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New output directory; never overwritten")
    parser.add_argument("--provider", required=True, help="MindTrial provider name")
    parser.add_argument("--model", required=True, help="Tool-capable model ID at that provider")
    parser.add_argument("--text-output", action="store_true",
                        help="Disable structured final output; keep the NEXUS tool enabled")
    args = parser.parse_args()
    try:
        prepare(args.directory, args.provider, args.model, args.text_output)
    except FileExistsError:
        parser.exit(1, "Choose a new directory; the existing run was left untouched.\n")
    print(f"Wrote {args.directory}/config.yaml and tasks.yaml. No model calls made.")
