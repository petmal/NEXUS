"""Player-facing records for sealed-facility-v3. Never consult truth or certificates."""

import json

REGISTER_WORLDS = {"stateful-discovery-v1", "stateful-planning-v1"}
REGISTER_GUIDE = (
    "Four machines, one display. Each machine updates only its own register. "
    "The seal displays x0, regardless of which mode you select. Gains and powers stay fixed. "
    "Other registers do not update automatically. Operate commits one step; probe predicts "
    "the display after that same step and leaves the seal unchanged. Each probe starts from "
    "the actual seal, not from another preview. Both cost one action. Observe is free. "
    "A reading of 5 signals collapse: a preview warns without causing it; an applied "
    "step that collapses the seal is permanent."
)

# Exact public sentences: never rewrite player IDs (for example sector R0) or formulas.
_TEXT = {
    "T1 STRUCTURAL THEORY": "STRUCTURAL THEORY",
    "T2 EFFECTIVE THEORY": "EFFECTIVE THEORY",
    "T3 MISSING RELATIONSHIP": "MISSING RELATIONSHIP",
    "T0/D0 means no hidden-law discovery; no solution procedure is supplied.": "No procedure is supplied.",
    "Coupling describes physical dependencies; at P3 travel also couples the tasks.": "Consult the map for apparatus locations.",
    "R0 has no environment action limit.": "Observe shows the remaining allowance; null means unlimited.",
    "R0 has no environment action cap. Other profiles expose their remaining allowance in status.": "Status shows the remaining allowance; null means unlimited.",
    "R2 allows the exact minimum total actions; R1 adds max(6,ceil(minimum/2)); R0 is uncapped.": "Status shows the remaining allowance; null means unlimited.",
    "R2 allows the exact minimum total actions; R1 adds max(6,ceil(minimum/2)); R0 has no action cap. ": "",
    "At R0 take still produces fresh identical specimens; there is no reset operation.": "Take produces fresh identical specimens; there is no reset operation.",
    "R0 removes in-game resource exhaustion; the external harness may still stop a run.\n": "",
    "R0 permits fresh specimens and unlimited game actions, subject to harness limits.\n": "",
    "unlimited; R0 remains subject to the\nharness limit.": "unlimited.",
    "In a disclosed T0 law": "In a supplied law",
}


def prose(text):
    for old, new in _TEXT.items():
        text = text.replace(old, new)
    return text


def contract(data):
    if "ontology" not in data:
        return data
    controls = data["apparatus"] = data.pop("ontology")
    for key in ("family", "experimental", "profile", "qualification_scope", "theory_level", "discovery_level"):
        controls.pop(key, None)
    return data


def local_record(public, filename, original):
    family = getattr(public.investigation, "ontology", None)
    if filename == "apparatus.txt" and family in {"compositional-repair-v1", "model-revision-v1"}:
        from nexus.presentation.laboratory import apparatus
        return apparatus(public)
    if filename == "apparatus.txt" and family == "staged-repair-v1":
        original = original.replace("from stores (or array in P0)", "from " + public.investigation.data().stock_room)
    if family is None and filename in ("theory.json", "facility_manual.txt") and "theory.json" in public.evidence_files:
        # Legacy manuals repeat their structural prior verbatim; keep the two records consistent.
        theory = public.evidence_files["theory.json"]
        prior = json.loads(theory)
        if isinstance(prior, dict) and ("level" in prior or "family" in prior):
            prior.pop("level", None)
            prior.pop("family", None)
            original = original.replace(theory, json.dumps(prior, sort_keys=True, indent=2))
    if filename != "theory.json":
        return prose(original) if filename.endswith((".md", ".txt")) else original
    data = json.loads(original)
    if not isinstance(data, dict):
        return original
    for key in ("axis_version", "family", "theory_level", "discovery_level", "experimental",
                "theory_disclosure", "profile", "profiles"):
        data.pop(key, None)
    spec = data.get("specification", {})
    # Describe the apparatus that is present, not its generator settings.
    if family in {"staged-repair-v1", "joint-assembly-v1"}:
        spec["linked_stages" if family == "staged-repair-v1" else "coupled_reader"] = spec["discovery"] != 3
        data.pop("disclosure", None)
    for key in ("theory", "discovery", "planning", "experimental"):
        spec.pop(key, None)
    if family == "representation-discovery-v1" and spec.get("known") is not None:
        data["known_order"] = ["source1", "source2", "kind0", "kind1", "kind2", "readout"]
    if family == "coupled-memory-v1" and spec.get("known") is not None:
        data["known_order"] = ["w", "a", "b", "c"]
    if family in REGISTER_WORLDS:
        data.pop("controls", None)
        data = {"instrument": REGISTER_GUIDE, **data}
    if "resolved_sampling" in data:
        if data.get("resolved") is None:
            del data["resolved_sampling"]
        else:
            data["resolved_sampling"] = ("The supplied treatment is the first accepted in selector order."
                                         if family == "compositional-repair-v1" else
                                         "The first equivalent program in selector order is supplied as resolved.")
    if "resolved_meaning" in data:
        data["resolved_meaning"] = "A non-null resolved vector gives the exact doses in order."
    # These strings also encode gameplay controls: remove only the operator wording.
    for key in ("gate_encoding", "controls"):
        if isinstance(data.get(key), str):
            data[key] = prose(data[key])
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def action_result(public, action, events, message, *, already_collapsed=False):
    """Project the copied public events; engine traces retain their exact original bytes."""
    family = getattr(public.investigation, "ontology", None)
    if action.type == "configure":
        from nexus.presentation.laboratory import configured
        message = configured(family, action.machine) or message
    for event in events:
        result = event["details"].get("result")
        if not isinstance(result, dict) or "ontology" not in result:
            continue
        result.pop("ontology")
        result.pop("version", None)
        if family in {"compositional-repair-v1", "model-revision-v1"} and action.type in ("probe", "operate"):
            from nexus.presentation.laboratory import result_message
            message = result_message(family, action, result["payload"]) or message
        if family not in REGISTER_WORLDS or action.type not in ("probe", "operate"):
            continue
        reading = result["payload"]["reading"]
        if action.type == "probe":
            message = f"Mode {action.machine} preview: seal display would read {reading}. Seal unchanged."
        else:
            message = f"Mode {action.machine} applied. Seal display reads {reading}."
        if reading == 5:
            message += (" Seal already collapsed." if already_collapsed else
                        " Warning: applying this mode would collapse the seal." if action.type == "probe"
                        else " The seal has collapsed.")
    return message
