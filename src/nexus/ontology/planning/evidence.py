"""Reuse the physical grammar; disclose the entire spatial planning problem."""

import json

from nexus.ontology.planning.layout import LAYOUTS
from nexus.ontology.planning.schema import FAMILY
from nexus.ontology.stateful.evidence import files as physics_files
from nexus.ontology.stateful.laws import MODES


def files(spec):
    theory = json.loads(physics_files(spec)["theory.json"])
    theory["family"] = FAMILY
    theory["controls"] = (
        "T0 discloses gains and powers in resolved. T3 retains all 256 laws. "
        "No profile supplies a solution procedure. The target and full map are public."
    )
    layout = LAYOUTS[spec.planning]
    return {
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "layout.json": json.dumps(
            {
                "rooms": layout.rooms,
                "undirected_edges": layout.edges,
                "machines": dict(zip(MODES, layout.mode_rooms)),
                "seal_start": layout.start,
                "finish_room": layout.finish,
                "visibility": "Complete map; no undisclosed rooms or routes.",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        "facility.txt": (
            "Align the original seal's coupled registers and return it to array. "
            "Read theory.json, layout.json and apparatus.txt. All routes are disclosed. "
            "Transformation order and travel can interact: minimizing operations alone "
            "need not minimize total actions."
        ),
        "apparatus.txt": (
            "Take seal before operating or probing it. Each mode is an unlimited-use "
            "machine at the location in layout.json. You must be in that room with the "
            "carried seal to use it. operate {machine,artifact} commits one update; "
            "probe with the same fields previews ONE update and its reading without "
            "changing the seal. There are no stocks, duplicate seals, resets, settings "
            "or measure action. take/drop/move work normally; wait changes no physics. "
            "Every accepted action, including movement and a rejected finish, costs "
            "one action. observe/status/manifest/evidence are free. Invalid actions "
            "are rejected without mutation. R0 has no environment action cap. Other "
            "profiles expose their remaining allowance in status. Finish requires "
            "the carried original seal in array with all four registers at the target. "
            "A failed finish leaves the seal unchanged. Its failure only constrains "
            "the law when the seal was carried in array. A display match alone is "
            "insufficient. Preserve the victory receipt after successful finish."
        ),
    }
