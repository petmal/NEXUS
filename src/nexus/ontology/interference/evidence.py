"""Public physical specification; no selection stratum, seed, proof or solution."""

import json

from nexus.ontology.interference.schema import FAMILY


def files(spec):
    return {
        "theory.json": json.dumps(
            {
                "family": FAMILY,
                "specification": spec.model_dump(mode="json"),
                "modulus": 5,
                "update": "Read the pre-operation vector. If x[guard_register] != guards[i], leave every register unchanged. Otherwise simultaneously set x[i]=(x[i]+gains[i])%5 and x[spill_register]=(x[spill_register]+spill_gains[i])%5. All other registers remain unchanged.",
                "controls": "Six registers in two banks of three. Every prerequisite, gain, write destination and current register is public. Guard, operated and spill registers are distinct. Independent spill writes stay local; coupled boundary modes redirect that write to the other bank. The number of reads/writes is unchanged. A previously matched coordinate can be disturbed. Every target must hold at once; there are no checkpoints or hidden laws.",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        "layout.json": json.dumps(
            {
                "rooms": ["array"],
                "undirected_edges": [],
                "machines": {c.machine: "array" for c in spec.topology},
                "seal_start": "array",
                "finish_room": "array",
                "visibility": "Complete map; all modes are co-located.",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        "facility.txt": "Read theory.json, layout.json and apparatus.txt. Carry the original seal, place every register at its exact target simultaneously, and finish in array. The seal payload always exposes the complete current vector.",
        "apparatus.txt": "Take seal before operating or probing. Operate {machine,artifact} with artifact seal commits one update. Probe with the same fields previews its entire resulting vector without changing the seal. An unmet prerequisite is an accepted unchanged-state operation/probe and costs one action. Each mode has unlimited uses. There are no stocks, duplicate seals, reset, configure or measure. Take/drop/move work normally; wait changes no physics. Every accepted action, including take, probe, wait and finish, costs one action. Invalid control requests are atomic and cost nothing. Observe/status/manifest/evidence are free. R2 allows the exact minimum total actions; R1 adds max(6,ceil(minimum/2)); R0 is uncapped. Reserve an action for finish. A failed finish leaves the vector unchanged. Success requires the original seal carried in array and every target matched. Preserve the issued victory receipt.",
    }
