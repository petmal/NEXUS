"""Prepare a one-model, one-control tutorial from the maintained MindTrial definitions."""

import argparse
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "nexus:first-run"
AUDITS = runpy.run_path(str(HERE / "audit_mounts.py"))


def prepare(directory, provider, model, text_output=False, image=IMAGE):
    config = json.loads((HERE / "nexus-fresh-world-luna-config.yaml").read_text())
    tasks = json.loads((HERE / "nexus-fresh-world-controls-tasks.yaml").read_text())
    settings = config["config"]
    # Use the known tool/service/validator contract; do not inherit Luna's inference settings.
    (backend,) = settings["providers"]
    backend["name"] = provider
    backend["runs"] = [{"name": model, "model": model, "disabled": False,
                        "max-requests-per-minute": 10, "disable-structured-output": text_output}]
    # For a named panel model, copy only its summary setting. Other models use provider defaults.
    for preset in HERE.glob("nexus-fresh-world-*-config.yaml"):
        (panel_provider,) = json.loads(preset.read_text())["config"]["providers"]
        (panel_run,) = panel_provider["runs"]
        if (provider, model) == (panel_provider["name"], panel_run["model"]):
            summary = {k: v for k, v in panel_run["model-parameters"].items()
                       if k in ("reasoning-summary", "thinking-summaries")}
            if summary:
                backend["runs"][0]["model-parameters"] = summary
            break
    for group in ("tools", "services", "validators"):
        for entry in settings[group]:
            entry["image"] = image
    settings["task-source"] = "./tasks.yaml"
    taskset = tasks["task-config"]
    (control,) = (row for row in taskset["tasks"] if row["name"] == "NEXUS fresh-F05")
    taskset["tasks"] = [control]
    # Tutorial limits are separate from the published panel and the world's action budget.
    taskset["max-turns"] = 40
    taskset["tool-selector"]["tools"][0]["max-calls"] = 32
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "private-audits").mkdir(mode=0o700)
    AUDITS["configure_service"](settings, "./private-audits")
    AUDITS["configure_tasks"](taskset)
    for name, data in (("config.yaml", config), ("tasks.yaml", tasks)):
        (directory / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New output directory; never overwritten")
    parser.add_argument("--provider", required=True, help="MindTrial provider name")
    parser.add_argument("--model", required=True, help="Tool-capable model ID at that provider")
    parser.add_argument("--text-output", action="store_true",
                        help="Disable structured final output; keep the NEXUS tool enabled")
    parser.add_argument("--image", default=IMAGE, help="Locally built NEXUS image tag or ID")
    args = parser.parse_args()
    try:
        prepare(args.directory, args.provider, args.model, args.text_output, args.image)
    except FileExistsError:
        parser.exit(1, "Choose a new directory; the existing run was left untouched.\n")
    print(f"Wrote {args.directory}/config.yaml and tasks.yaml. No model calls made.")
