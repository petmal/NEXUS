"""Complete compositional memory grammar, including synchronous timing."""

import json

from nexus.ontology.discovery.evidence import APPARATUS
from nexus.ontology.representation.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "specification": spec.model_dump(mode="json"),
        "resolved_construction": spec.resolved,
        "mission": "Install a memory cartridge on the actual carrier that produces exactly the facility's displayed trit for EVERY finite input history starting at zero. The checker compares complete reachable behavior, including histories longer than reader queries. Any behaviorally equivalent program is accepted; matching private parameter spelling is unnecessary. The cartridge receives the input pulses, never the facility's live output.",
        "arithmetic": "Values are 0,1,2, with all addition and multiplication modulo 3. Every allowed combination of the following primitive choices is possible and fixed for the episode.",
        "memory_grammar": {
            "initial": "Three memory cells r0,r1,r2 start at zero. On each input pulse x, ALL three update simultaneously from their OLD values.",
            "sources": "Cell0 source is x. Cell1 selects x (source1=0) or old r0 (source1=1). Cell2 selects x (source2=0), old r0 (source2=1), or old r1 (source2=2).",
            "update": "Each cell i chooses kind_i=0 (overwrite) or 1 (accumulate), and gain_i=1 or 2. New r_i = gain_i * selected_source_i + kind_i * old r_i, modulo3.",
            "view": "Readout=0 displays r2. Readout=1 displays r0+r1*r2 modulo3. Display is read AFTER all updates for the pulse.",
        },
        "assembler": {
            "settings_order": [
                "source1",
                "source2",
                "kind0",
                "kind1",
                "kind2",
                "gain0",
                "gain1",
                "gain2",
                "readout",
            ],
            "ranges": [[0, 1], [0, 2], [0, 1], [0, 1], [0, 1], [1, 2], [1, 2], [1, 2], [0, 1]],
            "effect": "Operate installs/replaces exactly these nine choices; no validation against the hidden facility occurs before finish.",
        },
        "reader": {
            "settings": "A sequence of 1..6 input trits, each0..2. No length prefix. These are pulses, not a build.",
            "result": "query repeats the sequence; values contains ONE final displayed trit. Every reader call starts an isolated zero-state reference fixture, applies all configured pulses, and reads only the final display. Intermediate outputs are not returned. Repeating a sequence gives the same result. This does not reset the live world or carrier.",
        },
        "theory_disclosure": "T3 hides wiring, update kinds, gains and readout, while disclosing the full primitive grammar above. T2 supplies known=[source1,source2,kind0,kind1,kind2,readout], leaving gains unknown. T0 supplies the complete resolved program. The D4 label is an experimental memory-structure profile; no particular experiment sequence is mandatory.",
    }
    return {
        "facility.txt": "The exit's memory cartridge is missing. Investigate the reference fixture and construct a cartridge that continues to behave correctly under every future input history. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": APPARATUS,
    }
