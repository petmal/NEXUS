"""Separate physical variation, persistent lab bias and operational disturbance."""

import json

from nexus.ontology.discovery.evidence import APPARATUS
from nexus.ontology.uncertainty.schema import FAMILY


def files(spec):
    from nexus.ontology.uncertainty.laws import target

    theory = {
        "family": FAMILY,
        "specification": spec.model_dump(mode="json"),
        "resolved_construction": target(spec.resolved) if spec.resolved is not None else None,
        "physical_grammar": "Five physical bits z0..z4 obey TWO independent XOR parity checks A·z=c and B·z=d. Mask bit j selects z_j; A,B are integers1..31. Sort the three nonzero masks A,B,A XOR B; the canonical A,B are the first two. Every one of those three masks has at least three set bits. c,d independently belong to{0,1}. Every admissible combination is possible. Exactly eight bit vectors satisfy the two checks. Physical signs are s_j=(-1)^z_j, so each is +1 or -1.",
        "loading_grammar": "Pattern0 has lambda=(+1,+1,+1,+1,+1); pattern1 has lambda=(+1,-1,+1,-1,+1). This is fixed throughout the episode and independent of the physical parity checks.",
        "three_distinct_quantities": {
            "physical": "s_j is the true physical sign in one of the eight allowed states.",
            "laboratory_display": "Lab y_j=s_j+lambda_j, using ORDINARY INTEGER addition. This is a persistent shared nuisance, not fresh independent noise. Repeated readings of a fixture do not average it away.",
            "operation": "During final operation, delta may be -1 OR +1. A live reference provides r=delta and sensor j provides y_j=s_j+lambda_j*delta. The device must work for EVERY allowed physical state AND BOTH delta values, not only for the lab case delta=+1.",
        },
        "reader": {
            "settings": "[mode,fixture], mode0..2, fixture0..7. Configure then probe/operate.",
            "mode0": "Returns the five lab values [y0,y1,y2,y3,y4] for that fixed fixture. The eight fixture IDs contain each allowed physical state exactly once in an arbitrary hidden order. EVERY permutation is possible. The assignment is persistent. All five values are measured jointly; no partial-channel action exists.",
            "mode1": "Returns five matched blank-reference values [lambda0,...,lambda4]. Fixture argument is ignored and canonicalized to0.",
            "mode2": "Returns EXACT balanced-panel summary: first5 means of y, next5 variances, next10 pairwise covariances in order(01,02,03,04,12,13,14,23,24,34). These use ordinary real-valued moment definitions; results here are exact integers. Fixture argument is ignored. This summary contains no higher-order moments or panel ordering.",
            "scope": "Reader measures the facility fixtures, not the installed build. values and query are indexed exactly as above. A cached reading is historical. Repeated fixtures reproduce the same joint vector, rather than providing an independent draw.",
        },
        "assembler": {
            "settings_order": ["mask", "offset", "pattern"],
            "ranges": [[0, 15], [0, 1], [0, 1]],
            "meaning": "Mask bit j (weights1,2,4,8) selects operational sensor j for j=0..3. Channel4 is the target and is NOT an input to the device. The candidate loading comes from pattern. For each selected channel form t_j=y_j-lambda_candidate_j*r using ordinary integer subtraction. Every selected t_j must be +1 or -1 in every operating case. Output=(-1)^offset times the PRODUCT of all selected t_j (empty product=1).",
        },
        "mission": "Carry the actual carrier in workshop with a compensator installed. Its output must equal the physical sign s4 for all eight actual physical states and both operational delta values, with valid corrected selected inputs in every case. Every robust valid build is accepted, including equivalent patterns on unused channels. Configure stores settings; assembler operate commits them; finish performs the complete check.",
        "theory_disclosure": "T3 hides checks, syndrome and loading pattern; its prior is exactly the complete compositional grammar above and all fixture permutations. T2 supplies known_checks and known_pattern, leaving the parity constants and fixture assignment unknown. T0 supplies resolved physical laws. D4 is an experimental dependence-construction profile. There is no required theory report or experiment order.",
    }
    return {
        "facility.txt": "A shared disturbance prevents the exit from opening. Build a compensator that predicts the fifth physical channel from the first four and the operational reference under every admissible disturbance. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": APPARATUS,
    }
