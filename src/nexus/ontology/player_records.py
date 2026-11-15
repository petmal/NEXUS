"""Read historical or current player records for the shipped reference strategies.

Reference code shares the validated physics models. Reconstruct their legacy profile
selectors from the *disclosed* law, reader and map, never from the compiled episode.
"""
import json


def specification(model, evidence, *, family):
    record = json.loads(evidence["theory.json"])["specification"]
    if "theory" in record:
        return model.model_validate(record)
    resolved = record.get("resolved") is not None
    known = any(record.get(k) is not None for k in
                ("known", "known_checks", "known_exponents", "known_kernel"))
    theory = 0 if resolved else 2 if known else 3
    if family in {"stateful-coordination-v1", "stateful-interference-v1", "stateful-planning-v1"}:
        from nexus.ontology.planning.layout import LAYOUTS
        rooms = tuple(json.loads(evidence["layout.json"])["rooms"])
        record["planning"] = next(i for i, layout in enumerate(LAYOUTS) if layout.rooms == rooms)
        discovery = 5 if family == "stateful-planning-v1" else 0
    elif family in {"staged-repair-v1", "joint-assembly-v1"}:
        linked = record.pop("linked_stages" if family == "staged-repair-v1" else "coupled_reader")
        discovery = 0 if resolved else 4 if linked else 3
    elif family in {"history-coupled-v1", "stateful-discovery-v1"}:
        discovery = 0 if record.get("procedure") is not None else 5
    else:
        discovery = 0 if resolved else 5 if family == "model-revision-v1" else 4
    return model.model_validate({**record, "theory": theory, "discovery": discovery})


def discovery_family(theory):
    if "family" in theory:
        return theory["family"]
    # Each reference interpreter handles a distinct public instrument grammar.
    for field, family in (("primitive_laws", "model-revision-v1"),
                          ("memory_grammar", "representation-discovery-v1"),
                          ("loading_grammar", "uncertainty-construction-v1"),
                          ("grammar", "coupled-memory-v1")):
        if field in theory:
            return family
    raise ValueError("unrecognized public reader grammar")
