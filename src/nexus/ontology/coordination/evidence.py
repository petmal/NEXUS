"""Complete public law, vector, target and map; never a seed or solution word."""

import json

from nexus.ontology.coordination.layout import layout_for
from nexus.ontology.coordination.schema import FAMILY


def files(spec):
    layout = layout_for(spec)
    return {
        "theory.json": json.dumps(
            {
                "family": FAMILY,
                "specification": spec.model_dump(mode="json"),
                "modulus": 3,
                "update": "x[i] = (x[i] + gains[i]*(1 + x[local_next]**powers[i] + cross)) % 3",
                "cross": "0 when cross_first is null; otherwise x[cross_first] before the update",
                "controls": (
                    "Every law and every current register is public. T0/D0 means no hidden-law "
                    "discovery; no solution procedure is supplied. Only the operated coordinate "
                    "changes. Local next-register rings remain in both coupling conditions. "
                    "Coupled boundary modes add a next-bank input; they do not replace an edge. "
                    "There is no collapse, reset, or checkpoint. All targets must hold together."
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        "layout.json": json.dumps(
            {
                "rooms": layout.rooms,
                "undirected_edges": layout.edges,
                "machines": dict(
                    zip((item.machine for item in spec.topology), layout.mode_rooms, strict=True)
                ),
                "seal_start": layout.start,
                "finish_room": layout.finish,
                "visibility": "Complete map; no undisclosed rooms or routes.",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        "facility.txt": (
            "Coordinate the original seal's register banks and return it to array. Read "
            "theory.json, layout.json and apparatus.txt. The entire vector is visible in "
            "the seal payload. Match every coordinate to its exact target simultaneously. "
            "Coupling describes physical dependencies; at P3 travel also couples the tasks."
        ),
        "apparatus.txt": (
            "Take seal before operating or probing. Each coordinate machine has unlimited "
            "uses at its disclosed room. Operate {machine,artifact} with artifact seal commits "
            "one update. Probe with the same fields previews one full resulting vector "
            "without changing any register. Both require the carried original seal at the "
            "machine. There are no stocks, duplicate seals, reset, configure or measure. "
            "Take/drop/move work normally; wait changes no physics. Every accepted action "
            "including probe, travel and a failed finish costs one action. Invalid actions "
            "are atomic and cost nothing. Observe/status/manifest/evidence are free. R2 "
            "allows the exact minimum total actions; R1 adds max(6,ceil(minimum/2)); R0 "
            "has no action cap. Status shows remaining allowance. Finish succeeds only "
            "when the original seal is carried in array and every register equals its "
            "target. A failed finish leaves the vector unchanged. Preserve the victory receipt."
        ),
    }
