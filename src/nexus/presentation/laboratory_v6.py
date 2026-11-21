"""Public object roles and literal arithmetic; no measurements or solving advice."""

import json

from nexus.presentation.devices import public_catalog as previous_catalog
from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.presentation.laboratory_v5 import brief

STOCK = (
    "blank-stock is a supply of optional blank workpieces, not the reference device. "
    "take blank-stock creates a new carried workpiece and returns its ID. A workpiece "
    "can hold a cartridge and a stored reference reading, but cannot replace carrier at finish."
)
INVENTORY = (
    "q0 + q1 + q2 + q3 = 5 at all times, starting from [2,1,1,1]. "
    "The five packets are shared across the four reservoirs, not five in each."
)
TRANSFER = (
    "For each link, use the counts immediately before that transfer. The destination's "
    "parity sets the requested amount: 1 packet if even (including zero), 2 if odd. "
    "Transfer at most the source's available count. An empty source transfers 0. "
    "Subtract the transferred amount from source and add it to destination."
)
DISPLAY = (
    "The display is only q0 % 3. Equal displays need not mean equal q0 values or equal "
    "inventories. Within one word, every transfer uses the state left by the previous "
    "transfer. Each separate reader query starts from [2,1,1,1]."
)


def public_catalog(family):
    devices = previous_catalog(family)
    if family == REVISION:
        devices["reader"]["targets"] = (
            "Carry carrier or a blank workpiece taken from blank-stock in workshop. "
            "The target holds the reading when operated; it is not the device tested. "
            "The reference is built into reader. Configure needs no artifact."
        )
        devices["assembler"]["targets"] = (
            "Carry carrier or a blank workpiece in workshop. Either can hold a cartridge, "
            "but only the actual carrier satisfies the exit requirement. Configure needs no artifact."
        )
    elif family == REPAIR:
        # Wrong-material operations are legal no-ops, not validator rejections.
        for name in ("stage", "sensor", "doser"):
            target = "seal" if name == "doser" else "a survey"
            devices[name]["targets"] = (
                f"Works on carried {target} in array. Using the other material has no effect "
                "and still costs an action. Configure, where supported, needs no artifact."
            )
    return devices


def record(public, filename, original):
    family = getattr(public.investigation, "ontology", None)
    if family not in (REPAIR, REVISION):
        return original
    if filename == "facility.txt":
        return "YOUR TASK\n" + brief(public) + "\n\n" + original
    if filename == "apparatus.txt":
        if family == REVISION:
            original = original.replace(
                "blank-stock supplies survey copies, which cannot replace the mission carrier.", STOCK)
            original += "\nINVENTORY AND DISPLAY\n" + INVENTORY + "\n" + TRANSFER + "\n" + DISPLAY + "\n"
        else:
            original += (
                "\nMATERIALS\nStage and sensor work on surveys; doser works on seal. "
                "Using the other material has no effect and still costs an action.\n"
            )
        return original
    if filename != "theory.json":
        return original
    data = json.loads(original)
    data["devices"] = public_catalog(family)
    if family == REVISION:
        data["terms"]["blank-stock and workpiece"] = STOCK
        data["terms"]["reference device"] += " It is built into reader, not an artifact to collect."
        data["notation"].update(inventory=INVENTORY, transfer=TRANSFER, display=DISPLAY)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
