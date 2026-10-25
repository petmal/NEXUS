"""Export the fixed 40-execution screen only after source-bound qualification."""

from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from nexus.evaluation.artifacts import atomic_json
from nexus.evaluation.discovery import digest
from nexus.evaluation.td_cycle import Cycle
from nexus.ontology.revision.proof import require
from nexus.provenance import source_digest

TEMPLATE_SHA256 = "e75448f84e9c8cec4b3f161a7ce0911d95db4a62ee6f6c88f32d569ed6c53747"

PROMPT_CHECK = "Before installing or submitting a proposed construction, check its predicted outputs against every archived and observed reading. Revise any construction that contradicts those readings. Consistency with observed readings alone does not prove correctness."
CHECKER_HELP = "This condition supplies operation check with a build array. It reports only consistency with archived and previously observed reader outputs. It consumes a tool call but no world action. It does not test hidden correctness or include rejected-finish feedback."


def export(cycle: Cycle, preflight_path: Path, template_path: Path, output: Path, *, image: str):
    report = json.loads(preflight_path.read_text())
    require(report.get("version") == "td-cycle-preflight-v1", "unsupported preflight version")
    require(report.get("status") == "passed", "preflight is incomplete or blocked")
    require(report.get("source_sha256") == source_digest(), "preflight source is stale")
    require(report.get("matrix_sha256") == digest(cycle.model_dump()), "preflight matrix differs")
    require(
        [c["id"] for c in report.get("cells", [])] == [c.id for c in cycle.cases],
        "preflight inventory incomplete",
    )
    require(report.get("independent_proof", {}).get("passed") is True, "independent proof missing")
    proof = report["independent_proof"]
    require(
        all(
            proof.get(key) == value
            for key, value in {
                "programs": 20736,
                "states": 56,
                "behavior_classes": 748,
                "independent_transitions": 2322432,
                "independent_all_history_equivalence_checks": 20736,
                "independent_reading_checks": 381480,
            }.items()
        )
        and proof.get("laboratory_horizon_identifies_all_history_classes") is True,
        "independent proof coverage incomplete",
    )
    triple = report.get("balanced_triple", {})
    require(
        triple.get("ids") == ["01", "02", "03"]
        and all(
            triple.get(key) is True
            for key in (
                "public_evidence_identical",
                "all_words_through_length_three_identical",
                "distinct_full_behaviors",
            )
        ),
        "balanced triple qualification missing",
    )
    pairs = report.get("rival_pairs", [])
    require(
        [pair.get("ids") for pair in pairs] == [["06", "07"], ["08", "09"]]
        and all(
            pair.get("public_evidence_identical") is True
            and len(pair.get("shortest_distinguishing_word", [])) == 6
            for pair in pairs
        ),
        "rival pair qualification missing",
    )
    require(report.get("harness_template_sha256") == TEMPLATE_SHA256, "preflight harness differs")
    for case, cell in zip(cycle.cases, report["cells"]):
        require(
            all(cell.get(key) == value for key, value in case.model_dump().items()),
            "preflight case identity mismatch",
        )
        required_checks = {"expected_C", "expected_L", "common_action_budget", "certificate_replay"}
        if case.role == "horizon-contrast":
            required_checks.add("contrast_admission")
        checks = cell.get("checks", {})
        require(
            required_checks <= checks.keys() and all(value is True for value in checks.values()),
            "preflight checks missing or failed",
        )
        require(
            cell.get("minimum_reading_only_certificate") == case.expected_certificate
            and cell.get("L_star") == case.expected_horizon,
            "preflight coordinates differ",
        )
        variants = {"baseline"}
        if case.single_shot:
            variants.add("single-shot")
        if case.role == "consistency":
            variants.add("checker")
        policies = cell.get("public_policy", {})
        require(
            set(policies) == variants
            and all(
                p.get("supported_replayed_win") is True
                and type(p.get("actions")) is int
                and 1 <= p["actions"] <= (4 if case.role == "execution" else 18)
                for p in policies.values()
            ),
            "public policy replay missing or invalid",
        )
    require(
        sha256(template_path.read_bytes()).hexdigest() == TEMPLATE_SHA256,
        "harness template differs from the source-pinned contract",
    )
    template = json.loads(template_path.read_text())
    require(bool(image.strip()), "image reference required")
    output.mkdir(parents=True, exist_ok=True)
    batches = [
        ("baseline", "openai", cycle.cases),
        ("single-shot", "openai", tuple(c for c in cycle.cases if c.single_shot)),
        ("consistency-baseline", "google", (cycle.cases[9],)),
        ("consistency-prompt", "google", (cycle.cases[9],)),
        ("consistency-checker", "google", (cycle.cases[9],)),
    ]
    manifest = {
        "version": "td-cycle-export-v1",
        "source_sha256": report["source_sha256"],
        "matrix_sha256": report["matrix_sha256"],
        "preflight_sha256": sha256(preflight_path.read_bytes()).hexdigest(),
        "harness_template_sha256": sha256(template_path.read_bytes()).hexdigest(),
        "image_reference": image,
        "live_results": "not_run",
        "reserved_followups": 20,
        "executions": [],
        "files": {},
        "notes": [
            "Model aliases/settings are inherited from the previous operator config, not verified immutable provider snapshots.",
            "JSON files with .yaml extension use the YAML 1.2 subset; keep task/config pairs together.",
            "Local byte hashes bind artifacts, not a signed authenticity attestation. Archive this manifest with the result bundle.",
            "Mount only the configured request file into player tools. Do not expose this repository, operator manifest, seeds, preflight, or image filesystem to evaluated models.",
        ],
    }
    for batch, provider_name, cases in batches:
        config = deepcopy(template["config"])
        root = config["config"]
        provider = next(p for p in root["providers"] if p["name"] == provider_name)
        root["providers"] = [provider]
        require(
            len(provider["runs"]) == 1 and not provider["runs"][0]["disabled"],
            "exactly one enabled provider run required",
        )
        root["task-source"] = f"./{batch}-tasks.yaml"
        for key in ("tools", "services", "validators"):
            for item in root[key]:
                item["image"] = image
        checker = batch == "consistency-checker"
        if checker:
            request = root["tools"][0]["parameters"]["properties"]["request"]
            request["properties"]["operation"]["enum"].append("check")
            request["properties"]["build"] = {
                "type": "array",
                "items": {"type": "integer", "minimum": 0, "maximum": 11},
                "minItems": 4,
                "maxItems": 4,
                "description": "Required only for operation check: a complete four-link construction.",
            }
            request["description"] += "\n" + CHECKER_HELP
        tasks = deepcopy(template["tasks"])
        task_root = tasks["task-config"]
        base_task = task_root["tasks"][0]
        task_root["tasks"] = []
        task_root["max-turns"] = cycle.max_turns
        task_root["tool-selector"]["tools"][0]["max-calls"] = cycle.tool_call_limit
        for repeat in range(1, cycle.repeats + 1):
            for case in cases:
                task = deepcopy(base_task)
                execution_id = f"{batch}-{case.id}-r{repeat}"
                task["name"] = "NEXUS " + execution_id
                task["tags"] = [cycle.version, "model-revision-v1"]
                if batch == "consistency-prompt":
                    task["prompt"] += "\n" + PROMPT_CHECK + "\n"
                if checker:
                    task["prompt"] += "\n" + CHECKER_HELP + "\n"
                inputs = {
                    "axis-version": 2,
                    "science-family": "model-revision-v1",
                    "seed": str(case.seed),
                    "theory-level": 0 if case.role == "execution" else 3,
                    "discovery-level": 0 if case.role == "execution" else 5,
                    "planning-level": 0,
                    "resource-pressure": 1,
                    "budget-profile": "standard",
                    "generation-timing": True,
                    "extended-diagnostics": True,
                }
                task["tool-selector"]["service-inputs"]["nexus"] = inputs
                options = {
                    "guidance": case.guidance,
                    "finish_policy": "single" if batch == "single-shot" else "recoverable",
                    "consistency_check": "readings" if checker else "off",
                }
                inputs["ontology-options"] = json.dumps(options, separators=(",", ":"))
                task_root["tasks"].append(task)
                manifest["executions"].append(
                    {
                        "id": execution_id,
                        "case_id": case.id,
                        "batch": batch,
                        "repeat": repeat,
                        "seed": case.seed,
                        "role": case.role,
                        "provider": provider_name,
                        "model_config": deepcopy(provider["runs"][0]),
                        "options": options,
                        "prompt_sha256": sha256(task["prompt"].encode()).hexdigest(),
                        "service_inputs": deepcopy(inputs),
                    }
                )
        for filename, data in ((f"{batch}-config.yaml", config), (f"{batch}-tasks.yaml", tasks)):
            path = output / filename
            atomic_json(path, data)
            manifest["files"][filename] = sha256(path.read_bytes()).hexdigest()
    require(len(manifest["executions"]) == 40, "unexpected execution count")
    atomic_json(output / "operator-manifest.json", manifest)
    ledger = {
        "version": "td-cycle-run-ledger-v1",
        "export_manifest_sha256": sha256(
            (output / "operator-manifest.json").read_bytes()
        ).hexdigest(),
        "instruction": "Fill from actual harness/provider/image artifacts. Null means unobserved; never infer provider completion from a service shutdown.",
        "runs": [
            {
                "execution_id": r["id"],
                "status": "not_run",
                "started_at": None,
                "ended_at": None,
                "harness_version": None,
                "image_id": None,
                "image_repo_digest": None,
                "image_vcs_revision": None,
                "observed_source_sha256": None,
                "resolved_model_version": None,
                "provider_stop_reason": None,
                "provider_retries": None,
                "tool_calls": None,
                "world_actions": None,
                "receipt_validation": None,
                "terminal_classification": None,
                "log_files_sha256": {},
                "notes": None,
            }
            for r in manifest["executions"]
        ],
    }
    atomic_json(output / "run-ledger.json", ledger)
    return manifest
