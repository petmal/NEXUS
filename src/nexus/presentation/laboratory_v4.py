"""Clarify disclosed laboratory rules without selecting or solving hidden mechanisms."""

import json

from nexus.presentation.laboratory import REPAIR, REVISION, apparatus, result_message as previous_result

PREPARATION_NAMES = ("context", "x", "y", "z", "a", "b", "c", "d")
TREATMENT_NAMES = ("a", "b", "c", "d")
LINK_NAMES = ("mode0_first_link", "mode0_second_link", "mode1_first_link", "mode1_second_link")


def named_settings(values, names):
    return ", ".join(f"{name}={value}" for name, value in zip(names, values, strict=True))


def record(public, filename, original):
    family = getattr(public.investigation, "ontology", None)
    if family not in (REPAIR, REVISION):
        return original
    if filename == "apparatus.txt":
        guide = apparatus(public)
        if family == REPAIR:
            guide = guide.replace("mission conditions", "required test conditions")
            guide = guide.replace(
                "four conditions listed in theory.json.",
                "four fixed exit checks listed in theory.json. These are not sequential tasks. "
                "You choose laboratory inputs freely; the exit checks keep their listed "
                "context, x, y and z. The same a, b, c and d must pass every check.",
            )
            guide = guide.replace(
                "Context is a stage setting, separate from the facility phase shown by look.",
                "Context is a stage setting, separate from the facility phase shown by look.\n"
                "Context 1 changes exactly one function inside the shared graph AND adds d\n"
                "to the final response. Setting d=0 removes only that offset; the changed\n"
                "function is still used. Context 0 always uses its original functions.",
            )
        else:
            guide = guide.replace(
                "Indices run from 0 to 11 in links_in_index_order.",
                "Indices run from 0 to 11 in links_in_index_order: index 0 means the first\n"
                "listed link. Each pair is [source,destination], naming reservoir numbers.\n"
                "The four slots are mode0_first_link, mode0_second_link, mode1_first_link,\n"
                "mode1_second_link. A link may be selected more than once.",
            )
            guide = guide.replace(
                "The four selected links stay fixed in the cartridge;",
                "A mode applies its first transfer, then its second transfer to the resulting\n"
                "inventory. min means the smaller value; % is the remainder. Reservoir\n"
                "counts are ordinary integers, not modulo 3. Only the final q0 display is\n"
                "reduced modulo 3. The four selected links stay fixed in the cartridge;",
            )
            guide = guide.replace(
                "Matching a few observed readings is not itself\na pass.",
                "The empty word means no transfers from the initial inventory; it is part of\n"
                "the finish requirement, but the reader accepts only nonempty words.\n"
                "Matching a few observed readings is not itself a pass.",
            )
            guide += (
                "\nRECORDS\nArchive entries are trusted reference measurements, each starting afresh.\n"
                "If a provisional_model is supplied, it is an unverified explanation that\n"
                "fits that archive, not an extra law or an installed cartridge. A supplied\n"
                "resolved_construction, when present, is a valid cartridge design.\n"
            )
        example = "configure stage [0,0,0,0,0,0,0,0]" if family == REPAIR else "configure reader [0,1,0]"
        return guide + (
            "\nCONSOLE INPUT\nConfigure accepts space-separated integers or a JSON integer array,\n"
            f"for example {example}.\n"
            "Use the listed ranges; out-of-range settings are rejected, not reduced modulo.\n"
        )
    if filename != "theory.json":
        return original
    data = json.loads(original)
    if family == REPAIR:
        data["field"] = "Every primitive and intermediate calculation uses modulo 3; values are 0,1,2. For example, -1 modulo 3 is 2."
        data["notation"] = {
            "graphs": "The three graphs are alternative wiring patterns. One fixed pattern applies in both contexts.",
            "nodes": "n1, n2 and n3 are intermediate values computed for a preparation, not persistent registers. The sensor returns only the final response.",
            "arguments": "u is the first argument and v is the second: g(n1,z) uses u=n1 and v=z.",
            "choices": "f, g and h each select a primitive independently. The same primitive may be used more than once.",
        }
        data["context"] = (
            "Context 0 uses f,g,h. In context 1, exactly one of f,g,h uses a different "
            "primitive from the same list; the other two functions and the graph stay the same. "
            "This replacement is fixed, not chosen again for each experiment. Switching back "
            "to context 0 restores its original functions. Both contexts are available immediately. "
            "Separately, context*d adds an output offset. d=0 removes that offset only; "
            "it does not undo the function replacement."
        )
        data["response"] = "(n3(context,x,y,z,a,b) + c + context*d) modulo 3; n3 is computed using that context's functions in the shared graph."
        data["settings_order"] = {"stage": PREPARATION_NAMES, "doser": TREATMENT_NAMES}
        data["goal"] = (
            "Apply one common [a,b,c,d] to the seal. The mission rows are fixed exit checks, "
            "not sequential tasks: every listed response must be 0. Laboratory inputs are "
            "freely configurable; exit-check inputs are fixed. At least one treatment exists, "
            "possibly several. Any satisfying treatment wins; there is no private preferred answer."
        )
    else:
        data["notation"] = {
            "word": "A word is a sequence of modes, executed left to right. Each mode executes two transfers in order.",
            "operators": "min(a,b) is the smaller value; a%b is the remainder. Reservoir inventories are ordinary nonnegative integers. Only the stated remainder operations are modular.",
            "link_indices": "Indices are zero-based: 0 selects the first links_in_index_order entry. Each entry is [source,destination], with reservoir numbers 0..3. Repeated link selections are allowed.",
            "empty_word": "The empty word performs no transfers from the initial inventory. Finish includes it; the reader accepts only words of length 1..8.",
            "records": "Archive measurements are trusted. A non-null provisional_model is an unverified explanation, not a law or an installed cartridge. A non-null resolved_construction is a supplied valid design.",
        }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def result_message(family, action, payload):
    message = previous_result(family, action, payload)
    if family == REPAIR:
        if action.machine in ("stage", "sensor") and payload["material"] == "survey":
            message += " Settings: " + named_settings(payload["settings"], PREPARATION_NAMES) + "."
            if action.machine == "stage":
                message += " No measurement taken; use sensor to measure the prepared survey."
        elif action.machine == "doser" and payload["material"] == "seal":
            message += " Treatment: " + named_settings(payload["doses"], TREATMENT_NAMES) + "."
    return message
