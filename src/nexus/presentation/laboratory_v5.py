"""Task-first orientation and uniform device records, independent of the hidden world."""

import json

from nexus.presentation.devices import public_catalog
from nexus.presentation.laboratory import REPAIR, REVISION

TASKS = {
    REPAIR: {
        "objective": "Prepare one treatment for the portable seal so it passes all four fixed exit checks.",
        "what_you_control": "You choose four treatment settings [a,b,c,d]. Survey specimens let you measure responses to laboratory preparations; the seal is the part submitted at the exit.",
        "what_you_investigate": "The records describe the possible calculation rules. The two operating contexts share a graph, but one function differs between them.",
        "success": "Apply the same treatment to seal, carry it in array and call finish. Its response must be 0 at every listed context and input. Any treatment that passes all checks is accepted.",
    },
    REVISION: {
        "objective": "Build a replacement routing cartridge whose displayed behavior matches the facility's reference device.",
        "what_you_control": "You choose four directed links: two for mode 0 and two for mode 1. The assembler installs this design as a cartridge on carrier.",
        "what_you_investigate": "The reference device moves five packets between four reservoirs. Each of its two modes executes two fixed links. The reader runs your chosen mode sequence on the reference from its initial inventory and reports one final display. The records state the transfer rule and what construction information is supplied.",
        "success": "Carry carrier in workshop with a cartridge installed and call finish. Starting at the same initial inventory, it must match the reference's final display for every finite sequence of modes, including the empty sequence. Different wiring is accepted if its displayed behavior always matches.",
    },
}

TERMS = {
    REPAIR: {
        "seal": "The portable part that receives your final treatment.",
        "treatment": "Four settings [a,b,c,d], applied together. The same values are used at every exit check.",
        "survey": "A reusable specimen for measurements; take stock to obtain one.",
        "preparation": "A survey's applied [context,x,y,z,a,b,c,d] settings.",
        "primitive and function": "A primitive is a listed calculation rule with ordered inputs u,v. Each function f,g,h selects a primitive; repeated choices are allowed.",
        "graph and intermediate values": "A graph specifies how f,g,h are connected. The values n1,n2,n3 are computed afresh for each preparation; they are not stored registers.",
        "context": "One of two operating conditions. Context 1 replaces one function and separately adds the output offset d.",
        "exit checks": "Four fixed test conditions, all of which one treatment must pass. They are not sequential tasks.",
    },
    REVISION: {
        "reference device": "The facility's original device, whose displayed behavior the replacement must match.",
        "reservoir and packet": "A reservoir holds a nonnegative integer number of packets. q0,q1,q2,q3 are the four counts; their sum stays five.",
        "directed link": "An ordered [source,destination] reservoir pair. Its transfer amount follows the supplied rule.",
        "mode": "Mode 0 or mode 1. Each executes two links in order; the second uses the inventory left by the first.",
        "sequence or word": "A list of mode numbers, executed left to right. Each reader query starts afresh; queries do not continue one another.",
        "display": "The final q0 % 3 value, not the complete inventory.",
        "cartridge and carrier": "A cartridge holds your four-link design. Carrier is the portable artifact on which you install it for submission.",
    },
}


def brief(public):
    task = TASKS.get(getattr(public.investigation, "ontology", None))
    return "\n\n".join(task.values()) if task else None


def record(public, filename, original):
    family = getattr(public.investigation, "ontology", None)
    if family not in TASKS:
        return original
    if filename == "apparatus.txt":
        return (brief(public) + "\n\nDEVICE REFERENCE\n"
                "theory.json lists each device's purpose, settings, targets, action effects and one "
                "independent usage example. In the local console, help DEVICE shows that entry. "
                "Examples describe syntax and immediate effects only. They are not an experiment "
                "sequence, a tested construction or a source of response values.\n\n" + original)
    if filename != "theory.json":
        return original
    data = json.loads(original)
    if family == REVISION:
        # Consolidate device instructions without dropping the per-episode finish policy.
        data.pop("assembler")
        data.pop("reader")
        data["submission"] = {
            "requirements": data["mission"],
            "on_rejection": data.get("finish_policy", {}).get("contract", "Failed eligible finishes are binary and recoverable while actions remain."),
            "feedback": "No hidden counterexample or component diagnosis is returned. An ineligible finish does not test a cartridge.",
        }
    else:
        data.pop("settings_order", None)
    return json.dumps({"task": TASKS[family], "terms": TERMS[family],
                       "devices": public_catalog(family), **data}, ensure_ascii=False, separators=(",", ":"))
