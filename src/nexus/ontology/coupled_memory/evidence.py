"""Complete public grammar; physical state and displayed signal are distinct."""

import json

from nexus.ontology.discovery.evidence import APPARATUS
from nexus.ontology.coupled_memory.laws import WIRINGS
from nexus.ontology.coupled_memory.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "specification": spec.model_dump(mode="json"),
        "resolved_construction": spec.resolved,
        "mission": "Install on the actual carrier a predictive cartridge whose displayed signal equals the facility reference for EVERY finite pulse history from the stated initial state, including the empty history and histories longer than laboratory queries. Equivalent programs are accepted. The cartridge receives pulses only, never the facility's live signal. Carry it in workshop and finish.",
        "state": "Hidden state is (q0,q1,q2,h,k), initially (2,1,1,0,0). q are nonnegative integer packet counts with q0+q1+q2=4 always. h,k are hidden memory cells in {0,1,2}; they are not conserved quantities. A displayed reading is neither a packet count nor a transfer amount.",
        "grammar": {
            "parameters": "Every combination of wiring w=0..5; rate a, feedback b, recurrence c in {0,1}; encoder gains u,v in {1,2}; encoder cross term z in {0,1} is allowed. All choices are fixed for the episode.",
            "wirings_in_index_order": WIRINGS,
            "pulse": "For input x in {0,1,2}, source=wirings[w][x], destination=wirings[w][(x+1)%3]. The third reservoir is unchanged.",
            "transfer": "Using OLD state, f=min(q_source, 1 + ((k + (1+a)*q_destination + b*h) % 2)). Set new q_source=old q_source-f and new q_destination=old q_destination+f.",
            "memory": "Simultaneously set new h=(old h+f+c*old q_destination)%3; new k=(old k+old h+b*f)%3. k uses OLD h; h uses OLD destination, not the transferred values.",
            "display": "After the complete update, y=(u*q0+q1+v*h+k+z*q0*k)%3 using the NEW state. For the empty history use initial state. Encoder parameters affect display only. Memory affects both later transfers and display.",
            "arithmetic": "Only expressions explicitly marked %2 or %3 are modular. q and f use ordinary nonnegative integer arithmetic. min clips transfer to available packets. No noise or rounding.",
        },
        "reader": {
            "settings": "A word of 1..4 pulses, each 0..2, without a length prefix.",
            "result": "values contains ONE final displayed trit. Each call applies the word to an isolated reference starting at (2,1,1,0,0). Intermediate outputs and hidden state are not returned. Repeating a word returns the same result. The live world and carrier are not reset or checked by the reader.",
        },
        "assembler": {
            "settings_order": ["w", "a", "b", "c", "u", "v", "z"],
            "ranges": [[0, 5], [0, 1], [0, 1], [0, 1], [1, 2], [1, 2], [0, 1]],
            "effect": "Configure stores seven choices. Operate installs/replaces them on the named artifact. Probe previews installation but neither commits nor tests correctness. Only finish tests the actual carrier against all histories.",
        },
        "theory_disclosure": "T3 supplies this complete bounded prior but hides all choices. T2 supplies known=[w,a,b,c], leaving the display encoder unknown. T0 supplies resolved_construction. D4 is an experimental feedback-memory profile, not a promise that every solution needs a long investigation.",
    }
    return {
        "facility.txt": "The sealed facility's transfer lattice has lost its predictive cartridge. Circulating packets leave traces in two memory cells, changing later transfers. Reconstruct its observable behavior to restore the exit interlock. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": APPARATUS,
    }
