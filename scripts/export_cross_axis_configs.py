"""Export the versioned, family-neutral MindTrial contract for the cross-axis pilot.

JSON is a YAML subset and lets the package runner stay standard-library only.
The historical T/D template is an immutable input; no historical export changes.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_SHA256 = "e75448f84e9c8cec4b3f161a7ce0911d95db4a62ee6f6c88f32d569ed6c53747"
IMAGE = "nexus:cross-axis-v1"
DESCRIPTION = """Interact with one persistent NEXUS world. State persists across calls; there is no reset.
The current manifest and listed evidence define the mission, laws, apparatus, observations,
valid identifiers, settings and action costs. Read them before acting.

CALL FORMAT: every tool call has one outer argument named request. Keep that wrapper.
Complete syntax examples (replace placeholder identifiers with values disclosed by this world):
{"request":{"operation":"manifest"}}
{"request":{"operation":"observe"}}
{"request":{"operation":"evidence","filename":"<listed-file>"}}
{"request":{"operation":"action","action":{"type":"take","artifact":"<listed-artifact-or-stock>"}}}
{"request":{"operation":"action","action":{"type":"operate","machine":"<listed-machine>","artifact":"<carried-artifact>"}}}
{"request":{"operation":"action","action":{"type":"configure","machine":"<configurable-machine>","settings":[0]}}}
The configure example illustrates JSON syntax only. Use the exact setting count, order and
allowed values disclosed for that apparatus; some worlds have no configurable apparatus.

REQUESTS: manifest, observe and status need only operation. evidence also needs filename;
action also needs an action object. Public reads do not spend world actions, but every tool
invocation counts toward the harness call allowance.

ACTION FIELDS: observe/wait/finish need type only; move also needs target (an adjacent room ID);
take/drop also need artifact; operate/probe also need machine and artifact; configure also
needs machine and settings (an ordered integer array). Use only capabilities disclosed for
the current world. Taking from a designated stock creates a specimen and returns its ID;
use that returned ID later. Taking an individual artifact retrieves it. Configure changes
apparatus settings without applying them. Operate commits the disclosed preparation,
measurement or transformation on a carried artifact. Probe previews the disclosed apparatus
without committing the specimen change; it still spends an environment action.

Track artifact history, apparatus settings, location and remaining allowance. A null world
budget means unlimited within NEXUS, subject to the harness limits. Finite hypothesis
enumeration is allowed. Only this NEXUS tool is available; no external computation or source
access is available. Follow the public evidence status and complete acceptance rule.
Satisfy the entire goal simultaneously, return to the disclosed finish location if required,
and call finish. A successful finish returns victory_code; return exactly that actual receipt
without explanation, quotes or Markdown. A rejected finish is not success; inspect the
resulting state and remaining budget. Terminal worlds cannot be reset.
"""


def provider(name, models):
    runs = []
    for model in models:
        google = name == "google"
        runs.append(
            {
                "name": f"{model} ({'high thinking' if google else 'medium reasoning'}) - cross-axis",
                "disabled": False,
                "model": model,
                "max-requests-per-minute": 3 if google else 20,
                "model-parameters": {"thinking-level": "high", "thinking-summaries": "auto"}
                if google
                else {"reasoning-effort": "medium", "reasoning-summary": "auto"},
            }
        )
    return {
        "name": name,
        "retry-policy": {"max-retry-attempts": 0, "initial-delay-seconds": 30},
        "client-config": {"api-key": ""},
        "runs": runs,
    }


def configurations():
    raw = (ROOT / "examples/mindtrial/td-cycle-harness.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != TEMPLATE_SHA256:
        raise ValueError("historical T/D harness template changed; review the contract")
    base = json.loads(raw)["config"]["config"]
    base.update(
        {
            "log-file": "./results/{{.Year}}-{{.Month}}-{{.Day}}/{{.Hour}}-{{.Minute}}-{{.Second}}.log",
            "output-dir": "./results/{{.Year}}-{{.Month}}-{{.Day}}/",
        }
    )
    tool = base["tools"][0]
    tool["description"] = DESCRIPTION
    tool["parameters"]["properties"]["request"]["description"] = (
        "Required outer request argument. Example complete tool call: "
        '{"request":{"operation":"manifest"}}. Set filename only for evidence; '
        "set action only for action. Use the current public contract for identifiers and settings."
    )
    tool["command"] += ["--tool-argument", "request"]
    for kind in ("tools", "services", "validators"):
        base[kind][0]["image"] = IMAGE
    result = {}
    for stage in ("canary", "rerun", "smoke"):
        config = copy.deepcopy(base)
        config["task-source"] = (
            f"./nexus-cross-axis-{'smoke-td' if stage == 'smoke' else stage + '-core'}-tasks.yaml"
        )
        config["providers"] = [
            provider(
                "openai", ["gpt-6-luna"] if stage == "smoke" else ["gpt-6-astra", "gpt-6-luna"]
            )
        ]
        if stage != "rerun":
            config["providers"].append(provider("google", ["gemini-3.8-flash"]))
        result[f"nexus-cross-axis-{stage}-config.yaml"] = {"config": config}
    return result


if __name__ == "__main__":
    for name, config in configurations().items():
        (ROOT / "examples/mindtrial" / name).write_text(json.dumps(config, indent=2) + "\n")
