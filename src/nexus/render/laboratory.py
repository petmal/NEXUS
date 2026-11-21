"""Readable views of public laboratory records; no inference or access to world truth."""

import json

from rich.table import Table
from rich.text import Text

from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.presentation.laboratory_v4 import LINK_NAMES, PREPARATION_NAMES, TREATMENT_NAMES, named_settings


def item_details(family, item, *, stock=False, roles=False):
    if family not in (REPAIR, REVISION):
        return None
    if stock:
        if not roles:
            return None
        supply = "Blank workpiece supply; not the reference device" if family == REVISION else "Reusable survey supply"
        remaining = "unlimited" if item.remaining is None else str(item.remaining)
        return (f"Location: {item.location}\n{supply}\nRemaining: {remaining}\n"
                f"take {item.id} creates one carried specimen and returns its ID.")
    data = item.model_dump(mode="json")
    if "payload" in data:
        payload = data["payload"]
        lines = [f"Location: {data['location']}"]
        if family == REPAIR:
            if payload["material"] == "seal":
                dose = payload["doses"]
                lines += ["Portable seal", "Applied treatment: " + (
                    "none" if dose is None else named_settings(dose, TREATMENT_NAMES))]
            else:
                lines += ["Reusable survey", "Applied preparation: " + named_settings(payload["settings"], PREPARATION_NAMES)]
                value = payload["reading"]
                lines += ["Stored sensor reading: " + ("not measured since preparation" if value is None else str(value))]
        else:
            if roles:
                lines += ["Mission carrier" if item.id == "carrier" else
                          "Blank workpiece; cannot replace carrier at finish"]
            build, reading = payload["build"], payload["reading"]
            lines += ["Installed cartridge: " + ("none" if build is None else named_settings(build, LINK_NAMES))]
            lines += ["Stored reference reading: " + ("none" if reading is None else
                      f"word {reading['query']} -> {reading['values'][0]}")]
            lines += ["Reference readings do not test the installed cartridge."]
        return "\n".join(lines)
    if "room_id" in data:
        uses = data["uses_remaining"]
        lines = [f"Room: {data['room_id']} | Uses left: {'unlimited' if uses is None else uses}"]
        settings = data.get("settings")
        if settings is not None:
            names = {"stage": PREPARATION_NAMES, "doser": TREATMENT_NAMES, "assembler": LINK_NAMES}.get(item.id)
            values = named_settings(settings, names) if names else str(settings)
            lines += [("Selected reference word: " if item.id == "reader" else "Pending settings: ") + values]
        return "\n".join(lines)
    return None


def render_theory(content, family, console):
    """Keep every supplied field, formatting existing graphs and fixed checks as tables."""
    data = json.loads(content)
    if family not in (REPAIR, REVISION) or not isinstance(data, dict):
        console.print_json(content)
        return
    if task := data.pop("task", None):
        console.print("YOUR TASK", style="bold")
        for text in task.values():
            console.print(text, markup=False, highlight=False)
    if terms := data.pop("terms", None):
        table = Table(title="Terms used in this task")
        table.add_column("Term")
        table.add_column("Meaning")
        for term, meaning in terms.items():
            table.add_row(Text(term), Text(meaning))
        console.print(table)
    if devices := data.pop("devices", None):
        for name, device in devices.items():
            render_device(name, device, console)
        console.print("DETAILED RULES", style="bold")
    if family == REPAIR:
        graphs, checks = data.pop("graphs"), data.pop("mission")
        console.print_json(data=data)
        table = Table(title="Possible graphs (one shared wiring pattern)")
        for label in ("Graph", "First calculation", "Second calculation", "Third calculation"):
            table.add_column(label)
        for i, graph in enumerate(graphs, 1):
            table.add_row(str(i), *(Text(part.strip()) for part in graph.split(";")))
        console.print(table)
        table = Table(title="Fixed exit checks: one treatment must pass every row")
        for label in ("Check", "Context", "x", "y", "z", "Required response"):
            table.add_column(label)
        for i, check in enumerate(checks, 1):
            table.add_row(str(i), str(check["context"]), *map(str, check["input"]), str(check["response_required"]))
    else:
        links = data["primitive_laws"].pop("links_in_index_order")
        console.print_json(data=data)
        table = Table(title="Link indices (source -> destination)")
        for label in ("Index", "Source reservoir", "Destination reservoir"):
            table.add_column(label)
        for i, (source, destination) in enumerate(links):
            table.add_row(str(i), f"q{source}", f"q{destination}")
    console.print(table)


def render_device(name, device, console):
    """One public device definition serves both theory and help; examples are not run."""
    console.rule(Text(name))
    console.print(device["description"], markup=False, highlight=False)
    console.print("Targets: " + device["targets"], markup=False, highlight=False)
    settings = device["settings"]
    if settings is None:
        console.print("Settings: none; this device does not accept configure.")
    else:
        console.print("Settings: " + settings["description"], markup=False, highlight=False)
        schema = settings["schema"]
        table = Table(title=f"{schema['minItems']}..{schema['maxItems']} settings")
        for label in ("Parameter", "Allowed integers", "Meaning"):
            table.add_column(label)
        constraints = schema.get("prefixItems", [schema.get("items")])
        for parameter, constraint in zip(settings["order"], constraints, strict=True):
            meaning = settings["parameters"][parameter]
            table.add_row(Text(parameter), f"{constraint['minimum']}..{constraint['maximum']}", Text(meaning))
        console.print(table)
    for action in ("configure", "probe", "operate"):
        if (description := device["actions"].get(action)) is None:
            continue
        console.print(f"{action} ({description['action_cost']} action): " + description["effect"], markup=False, highlight=False)
        console.print("Returns: " + description["returns"], markup=False, highlight=False)
    for example in device["examples"]:
        action = example["action"]
        args = json.dumps(action["settings"]) if action["type"] == "configure" else action["artifact"]
        console.print("Standalone usage example", style="bold")
        console.print("Requires: " + example["requires"], markup=False, highlight=False)
        console.print(f"{action['type']} {action['machine']} {args}", markup=False, highlight=False)
        console.print("Effect: " + example["effect"], markup=False, highlight=False)
