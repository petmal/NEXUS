"""Export separate model configs with the already evaluated per-model settings."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/mindtrial"
SOURCES = {
    "astra": ("nexus-cross-axis-canary-config.yaml", "openai", "gpt-6-astra"),
    "luna": ("nexus-cross-axis-canary-config.yaml", "openai", "gpt-6-luna"),
    "flash": ("nexus-cross-axis-canary-config.yaml", "google", "gemini-3.8-flash"),
    "grok": ("nexus-capability-smoke-grok-config.yaml", "xai", "grok-4.7"),
}


def export():
    files = {}
    for model, (source, provider_name, model_name) in SOURCES.items():
        config = json.loads((EXAMPLES / source).read_text())
        settings = config["config"]
        provider = next(p for p in settings["providers"] if p["name"] == provider_name)
        run = copy.deepcopy(next(r for r in provider["runs"] if r["model"] == model_name))
        run["name"] = run["name"].split(" - ")[0] + " - fresh worlds"
        provider["runs"] = [run]
        settings["providers"] = [provider]
        settings["task-source"] = "./nexus-fresh-world-controls-tasks.yaml"
        for section in ("tools", "services", "validators"):
            for item in settings[section]:
                item["image"] = "nexus:fresh-world-v1"
        files[f"nexus-fresh-world-{model}-config.yaml"] = config
    return files


if __name__ == "__main__":
    for name, value in export().items():
        (EXAMPLES / name).write_text(json.dumps(value, indent=2) + "\n")
