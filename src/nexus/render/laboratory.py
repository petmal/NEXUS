"""Readable views of public laboratory records; no inference or access to world truth."""

import json

from rich.table import Table
from rich.text import Text

from nexus.presentation.laboratory import REPAIR, REVISION
from nexus.presentation.laboratory_v4 import LINK_NAMES, PREPARATION_NAMES, TREATMENT_NAMES, named_settings


def item_details(family, item, *, stock=False):
    if family not in (REPAIR, REVISION) or stock:
        return None
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
