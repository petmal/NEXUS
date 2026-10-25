"""Player-complete primitive language and explicitly non-authoritative notebook."""

import json

from nexus.ontology.discovery.evidence import APPARATUS
from nexus.ontology.revision.laws import EDGES, INITIAL
from nexus.ontology.revision.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "specification": spec.model_dump(
            mode="json", exclude={"finish_policy", "consistency_check"}
        ),
        "resolved_construction": spec.resolved,
        "mission": "Install a routing cartridge on the actual carrier. Its displayed output must equal the facility reference for EVERY finite word of modes 0 and 1, including the empty word and words longer than the reader permits. Equivalent hidden constructions are accepted. Carry the carrier in workshop and finish successfully.",
        "primitive_laws": {
            "inventory": "Four reservoirs q0,q1,q2,q3 contain nonnegative integer packets. Their total is always five. Inventories are not modular.",
            "initial_inventory": INITIAL,
            "link": "A directed link (source,destination) transfers min(q_source,1+(q_destination%2)) packets. Subtract this amount from source and add the same amount to destination; other reservoirs are unchanged. Evaluate both quantities before this transfer.",
            "composition": "Each mode executes exactly TWO directed links in order. The second link uses the state AFTER the first link. Modes can share links and reservoirs; repeats are allowed. Nothing else changes the inventories. All four link choices are fixed throughout the episode.",
            "display": "After the complete word, the reader reports q0 % 3, one value in {0,1,2}. A display is not the full inventory or a transferred amount. There is no noise or rounding.",
            "construction_bounds": "Every ordered choice of four links from the following list is permitted. The first two define mode 0, and the last two define mode 1. These primitive rules and bounds are complete; derived apparatus responses and hidden wiring are not supplied.",
            "links_in_index_order": EDGES,
        },
        "archive": [
            {"word": [0], "display": spec.archive[0]},
            {"word": [1], "display": spec.archive[1]},
        ],
        "archive_semantics": "Each archived word starts from the stated initial inventory on its own reference fixture. Archive readings are exact trusted observations, not approximate predictions.",
        "reader": {
            "settings": "A word of 1..8 integers, each 0 or 1; no length prefix.",
            "result": "values contains ONE final display. Every query applies its complete word to an isolated fixture at the stated initial inventory. No intermediate readings are returned. This does not reset the live game or test your installed cartridge.",
        },
        "assembler": {
            "settings_order": [
                "mode0_first_link",
                "mode0_second_link",
                "mode1_first_link",
                "mode1_second_link",
            ],
            "ranges": [[0, 11]] * 4,
            "effect": "Configure stores four link indices; operate installs/replaces the cartridge. Probe previews installation without committing or checking correctness. Only finish checks the actual carried cartridge against all histories. Failed eligible finishes are binary and recoverable while actions remain.",
        },
        "provisional_model": spec.provisional,
        "provisional_status": "If present, this inherited four-link model explains the archive. It may be incomplete or correct; it is NOT an additional law or constraint on possible worlds. You may revise it or derive a model directly from the primitives and measurements. Preserve trusted archive predictions when revising.",
        "theory_disclosure": "T0 supplies resolved_construction. Experimental T3/D5 hides the composed mechanism. Guidance selects whether a provisional explanation accompanies the same trusted archive; it does not change the world, permitted constructions, reader, budget or success test.",
    }
    apparatus = APPARATUS
    if spec.finish_policy == "single":
        policy = (
            "The first rejected eligible finish with an installed cartridge on the carried "
            "carrier immediately ends the attempt, even with actions left. Ineligible "
            "finishes do not test a cartridge and remain recoverable."
        )
        theory["finish_policy"] = {"name": "single", "contract": policy}
        theory["assembler"]["effect"] = theory["assembler"]["effect"].replace(
            "Failed eligible finishes are binary and recoverable while actions remain.", policy
        )
        apparatus = apparatus.replace(
            "Failure reveals only a binary rejection and is recoverable while actions\n"
            "remain; no hidden counterexample or component diagnosis is returned.",
            policy + " No hidden counterexample or component diagnosis is returned.",
        )
    if spec.consistency_check == "readings":
        theory["consistency_assistance"] = {
            "request": {"operation": "check", "build": [0, 0, 0, 0]},
            "contract": "Returns only whether this construction matches the archive and all "
            "distinct reader outputs observed so far. It does not check unobserved words, "
            "failed finishes, hidden truth, or guaranteed success. No world action is charged; "
            "the harness tool-call limit still applies. Available only while active.",
        }
    return {
        "facility.txt": "The sealed facility's return lattice requires a replacement routing cartridge. Its local transfer elements obey exact primitive laws, but the composed routing is hidden. Derive and test an explanation that remains valid as the lattice changes state. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": apparatus,
    }
