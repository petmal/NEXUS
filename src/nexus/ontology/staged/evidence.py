"""Complete player rules, with baseline readings distinct from current loads."""

import json


def files(spec):
    theory = {
        "specification": spec.model_dump(mode="json"),
        "arithmetic": "All loads, tags, doses and arithmetic are modulo 3. Stages are numbered 0,1,2.",
        "mechanisms": "At each stage i: F_i(u)=(u+k_i)^e_i mod 3; k_i is in {0,1,2}, e_i is in {1,2}. Route r_i=(k_i+e_i-1) mod 3. Every combination is possible. No noise, hidden solvability filter or additional operator exists.",
        "public_function_menu": [
            {
                "shift": k,
                "exponent": e,
                "values_at_tags_0_1_2": [pow((u + k) % 3, e, 3) for u in range(3)],
            }
            for k in range(3)
            for e in (1, 2)
        ],
        "disclosure": "T2 supplies each exponent in specification.known_exponents, but shifts remain unknown. T3 hides both. T0 supplies exact mechanisms and the complete repair table.",
        "initial_state": "Each seal-i has immutable public tag i, cumulative doses [0,0,0], and hidden baseline loads [F_0(i),F_1(i),F_2(i)]. Stock-i makes survey copies with tag i and zero doses, never extra mission seals.",
        "reader": {
            "settings": "[stage,carrier], each in {0,1,2}",
            "active_carrier": "Always 0 at every stage."
            if not spec.linked
            else "0 at stage 0; r_(i-1) at stage i>0.",
            "result": "Reconstruct a fresh baseline COPY with the specimen's tag u. Return F_stage(u) if carrier is active, otherwise return 0. A zero reading does NOT disclose whether the carrier was active. Both probe and operate give the same reading; operate only caches it.",
            "scope": "Reading is the reference response of the fresh baseline copy, NOT a remaining-load measurement. The actual tag and doses never change. All settings and tags are legal throughout; there is no required order of experiments.",
        },
        "trimmer": {
            "settings": "Three doses [v0,v1,v2], each in {0,1,2}; configure only stores them and does not apply them.",
            "operate": "Adds v componentwise to this seal's cumulative doses d modulo 3. Dose entries are treatments applied, not measured hidden properties.",
            "remaining_loads": ["F_0(u)-d0", "F_1(u)-d1-r_0*d0", "F_2(u)-d2-r_1*d1"],
            "scope": "An earlier dose also disturbs the following load. Repeated treatments add. To change cumulative dose from old to desired, apply desired-old modulo 3. Probe previews public doses only and never commits them or reveals remaining loads.",
        },
        "anneal": "Operate anneal restores baseline loads by clearing all cumulative doses and cached reading. It preserves the tag, mechanism, evidence and spent actions; it is not an episode reset.",
        "mission": "Carry the actual seal-0, seal-1 and seal-2 in array, with all three hidden loads of EACH seal zero, then finish. Every valid treatment sequence counts. Survey copies do not substitute for seals.",
        "finish_feedback": "Success returns the actual victory receipt and ends play. Failure returns only binary rejection, no per-seal or per-load result. Rejections may be used as evidence and retried while budget remains.",
        "profile": "Axes v2, family-specific: D3 independently accessible experiments; D4 dependent reader contexts; D0 supplied execution solution. D3 and D4 have the same coupled physical repair. Numeric labels do not assert v1 probe-count guarantees.",
    }
    return {
        "facility.txt": "You are trapped in a staged array. Three exit seals carry three hidden loads each. Discover the artificial mechanisms, choose useful reference experiments, and apply treatments that clear every load. Treatment of an earlier load also affects the following load. Names carry no outside physical meaning. Read theory.json and apparatus.txt before acting.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take seal-0, seal-1, seal-2 from stores (or array in P0). Optional stock-0, stock-1, stock-2 provide fresh survey specimens. All apparatus is in array. Configure reader with [stage,carrier], then probe or operate reader on a carried specimen. Configure trimmer with three doses, then operate trimmer to apply them to a carried seal. Configure is NOT a controller submission or correctness test. Operate anneal restores one specimen to baseline. Probe never commits a transformation. Each take, move, configure, probe, operate, wait or finish costs one action. Manifest, evidence, observe and status are free. Invalid requests do not alter state or spend actions. Stock and apparatus use are unlimited; action budget is as advertised. There is no session reset. Call finish successfully and return exactly its actual victory_code.",
    }
