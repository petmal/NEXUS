"""Self-contained public theory: raw readings, physical response and reference scope."""

import json


def files(spec):
    theory = {
        "coupled_reader": spec.coupled,
        "field": "All values and arithmetic are modulo 3. Subtract modulo 3 as well.",
        "primitives_in_selector_order": ["u+v", "u-v", "u*v", "u*u+v"],
        "graphs_in_selector_order": [
            "n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n2,x)",
            "n1=f(x,y)+a; n2=g(y,z)+b; n3=h(n1,n2)",
            "n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n1,n2)",
        ],
        "contexts": "Context 0 uses f,g,h. Context 1 replaces exactly one with a different primitive. Topology and the other two primitives remain shared. Both contexts are immediately accessible.",
        "physical_response": "F(context,x,y,z,a,b)=n3+q. q is an unknown fixed trit shared by both contexts.",
        "unknowns": "Topology, f,g,h, replaced module, its replacement primitive, and q. Every combination in this grammar is possible. There is no solvability or difficulty filter.",
        "observation_model": (
            "E=reader_offset+n2 evaluated in the OTHER context, at the SAME x,y,z,a,b. Survey displays M=F+E. Reference displays M=E: its physical response is exactly zero while its companion upstream path is identical to the survey's. The multiplier of n2 is known to be 1. reader_offset is an unknown fixed trit. The reader does not disclose E, F, n1 or n2 separately."
            if spec.coupled
            else "Reader is calibrated: E=0. Survey displays M=F; reference displays 0."
        ),
        "reference_scope": "Matched survey and reference preparations share the same companion path and reader offset in every context, at every input and trim, throughout the episode. Different settings need not have the same E. Reuse is unlimited. Their raw displays must be interpreted using this contract; a reference reading is not itself the survey's physical response.",
        "mission": "Program the seal with [topology,f,g,h,changed,replacement,q]. changed 0/1/2 means f/g/h. Its countermechanism uses exactly the grammar above. At finish, the facility checks F_actual-F_program=0 for BOTH contexts and ALL x,y,z,a,b in {0,1,2}: 486 conditions. Reader contributions are irrelevant to this physical goal. Any behaviorally equivalent program wins; hidden spelling is not required.",
        "resolved": spec.resolved,
        "resolved_sampling": "In T0/D0 only, the first equivalent program in selector order is supplied as resolved. Otherwise no program is disclosed.",
        "status": "This is an exhaustive bounded prior and authoritative apparatus contract. There is no provisional law or unlisted interaction form to guess.",
    }
    return {
        "facility.txt": "You are confined to a counterphase array. An exit seal must cancel a mechanism across two phase contexts and every admissible excitation. Survey stock produces reusable specimens; reference stock produces matched specimens with suppressed physical output. Names carry no outside physical meaning. Read theory.json and apparatus.txt. Experiment in any order, then apply a counterprogram and carry the seal into array to finish.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take seal, stock, or reference-stock using ordinary take. Stocks persist and return new specimen IDs. Move to array if needed. Configure stage with [context,x,y,z,a,b]: context 0..1, other values 0..2. Operate stage on survey or reference to prepare it and clear its old reading. Probe or operate sensor on a prepared specimen returns ONE raw scalar display, with its material and preparation. Probe previews without changing the specimen. Configure doser with [topology,f,g,h,changed,replacement,q]: topology/changed/q 0..2, primitive selectors 0..3, replacement different from the selected original primitive. Operate doser on seal to apply this program; probe only previews. Configure alone never transforms an object. Seal has no sensor output; surveys/references do not accept counterprograms. All inputs and trims including mission conditions are legal from the start; no forced order, limited stock or apparatus wear. Finish checks only the full physical mission, returns binary rejection without a failing residual, and may be retried while budget remains. Carry seal in array to win. Mutating actions and probe/finish cost one action; observe, manifest, evidence and status are free. No reset.",
    }
