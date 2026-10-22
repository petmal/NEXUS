"""Player-safe contract. No construction seed, qualification result or selected law."""

import json

from nexus.ontology.stateful.laws import MODES
from nexus.ontology.stateful.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "specification": spec.model_dump(mode="json"),
        "mission": f"Carry the original seal in array with physical registers exactly {spec.target}, then finish. The reader alone does not certify this joint state.",
        "initial_state": [0, 0, 0, 0],
        "state": "Four physical registers x0,x1,x2,x3, each in 0..4. Only x0 is displayed. Histories are records of operations, not hidden register values.",
        "grammar": {
            "choices": "Each mode i has a fixed gain g_i in {1,2} and power p_i in {1,2}. Every one of the 256 combinations is in the public prior. Choices may differ between modes.",
            "mode_order": MODES,
            "update": "Mode i changes ONLY x_i: new x_i = (old x_i + g_i * (1 + old x_((i+1)%4)^p_i)) % 5. All other registers retain their old values. The superscript ^ means exponentiation, not XOR.",
            "coupling": "The loop closes: mode 3 depends on x0. Changes at a hidden register can affect the display through later operations on its predecessors.",
            "collapse": "If an operation produces (4,4,4,4), the seal collapses permanently. Thereafter every operation and probe reports 5 and the goal is unreachable. Value 5 is a collapse signal, not a register value.",
            "display": "After an operation the displayed reading is the actual NEW x0, or 5 on collapse. No noise or hidden display correction. A probe reports that same reading for a hypothetical next operation; it does not change the real seal.",
            "arithmetic": "All register updates use nonnegative remainder modulo 5. There is no global phase-dependent law and no spontaneous evolution.",
        },
        "scope": "This is a bounded artificial law-discovery and control problem. Finite hypothesis enumeration is valid. No outside physical analogy is needed.",
        "controls": "T0 discloses the gains and powers in resolved. D0 additionally supplies a procedure. T3 does not disclose their selected values. The exact physical goal is public in every profile.",
    }
    return {
        "facility.txt": "The exit lattice accepts one original seal. Its four coupled registers have lost their calibration. The seal is your only experimental subject and your exit key. Experiments change the very system you must eventually align. Read theory.json and apparatus.txt before acting.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take seal before operating it. All four modes are unlimited-use machines in array. operate {machine,artifact} commits one update; probe with the same fields previews ONE update and its reading without committing. There are no stocks, duplicate seals, resets, annealers, separate reference samples, configure settings, or measure action in this family. You may take/drop/move normally. wait changes no physics. Each successful action except observe costs one phase-shift; observe/status/manifest/evidence are free. R0 has no environment action limit. A rejected finish costs one action and leaves the seal unchanged; it discloses only that the joint goal failed. Finish requires the carried original seal in array. Do not substitute a display match for the complete goal. Preserve the actual victory receipt after successful finish.",
    }
