"""V7 player instructions distinguish mission objects from optional experiments."""


def record(public, filename, text):
    family = getattr(public.investigation, "ontology", None)
    if filename == "apparatus.txt":
        if family == "compositional-repair-v1":
            return text.replace(
                "COLLECT AND PREPARE\nTake seal and take stock. Stock remains available; the response names the new\nsurvey ID.",
                "Take seal for the exit.\n\nOPTIONAL SURVEY\nTo run a survey, take stock. "
                "Stock remains available and the response names the new survey ID.",
            )
        if family == "history-coupled-v1":
            return text.replace(
                "Take seal and/or take stock to receive a reusable survey specimen ID.",
                "Take seal for the exit. For a separate experimental specimen, take stock and use the returned ID.",
            )
        if family in ("coupled-transfer-v1", "coupled-evidence-v1"):
            return text.replace(
                "Take seal, stock, or reference-stock using ordinary take.",
                "Take seal for the exit. For experiments, take stock for a survey specimen "
                "or reference-stock for a reference specimen.",
            )
    elif filename == "manual.md":
        if family == "coupled-repair-v1":
            spec = public.investigation.data()
            return text.replace(
                f"Take seal and take stock in {spec.stock_room}. A stock take returns a fresh survey\n"
                f"specimen ID. Carry both into {spec.mission_room}. Use the returned survey ID.",
                f"Take seal in {spec.stock_room} and carry it to {spec.mission_room} for the exit.\n"
                f"For survey measurements, take stock in {spec.stock_room} and use the returned "
                f"specimen ID in {spec.mission_room}.",
            )
        if family == "coupled-dynamics-v1":
            return text.replace(
                "Take seal and take stock; stock returns a fresh survey ID. Carry the\nmaterials into array.",
                "Take seal and carry it into array for the exit.\n"
                "For an experiment, take stock and bring the returned survey specimen into array.",
            )
        if family == "causal-mechanisms-v1":
            return text.replace(
                "Take stock to create a fresh specimen. Use the returned specimen ID.",
                "For a bench experiment, take stock to create a fresh specimen and use its returned ID.\n"
                "The prediction board accepts settings independently of specimen collection or treatment.",
            ).replace("Operate pulse on that specimen to apply one history-dependent treatment.",
                      "To apply a history-dependent treatment, operate pulse on that specimen.")
    elif filename == "facility.txt":
        if family in ("coupled-transfer-v1", "coupled-evidence-v1"):
            return text.replace("Experiment in any order, then apply a counterprogram",
                                "Apply a counterprogram")
        if family == "staged-repair-v1":
            return text.replace("Discover the artificial mechanisms, choose useful reference experiments, and apply treatments",
                                "Reference experiments are available. Apply treatments")
        if family == "representation-discovery-v1":
            return text.replace("Investigate the reference fixture and construct a cartridge",
                                "The reference fixture is available for measurements. Construct a cartridge")
    return text
