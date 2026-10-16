"""Uniform player contract: artificial symbols, exact grammar, no selected truth."""

import json

from nexus.ontology.compositional.laws import MISSION


def files(spec):
    theory = {
        "field": "All arithmetic is modulo 3; values are 0,1,2.",
        "primitives": ["u+v", "u-v", "u*v", "u*u+v"],
        "mechanisms": "f,g,h independently select primitives; one unknown shared topology applies in both contexts.",
        "context": "Context 0 uses f,g,h. Context 1 replaces exactly one of them with a different primitive; the other two and topology are unchanged. Both contexts are available immediately.",
        "graphs": [
            "n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n2,x)",
            "n1=f(x,y)+a; n2=g(y,z)+b; n3=h(n1,n2)",
            "n1=f(x,y)+a; n2=g(n1,z)+b; n3=h(n1,n2)",
        ],
        "response": "n3+c+context*d modulo 3",
        "prior": "Complete bounded grammar: all three graphs, all independent primitive selections, every one-module different replacement. Exactly those worlds with at least one four-trit treatment satisfying the mission are possible. No other restriction. Equivalent worlds are retained.",
        "mission": [
            {"context": mode, "input": point, "response_required": 0} for mode, point in MISSION
        ],
        "goal": "Apply one common [a,b,c,d] to the seal. All four mission responses must vanish simultaneously. Any satisfying treatment wins; there is no private preferred answer.",
        "resolved_sampling": "If resolved is supplied (T0), it is the lexicographically first accepted treatment. Otherwise no treatment is disclosed.",
        "resolved": spec.resolved,
    }
    return {
        "facility.txt": "You are confined to the counterphase array. A seal must stabilize four excitations across two accessible phase contexts before the exit accepts it. Survey stock produces reusable specimens. The contexts share mechanisms, with one local replacement. Names carry no outside physical meaning. No experiment order is required. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take seal and take stock (response returns survey ID). Move to array if needed. Configure stage with [context,x,y,z,a,b,c,d]: context is 0 or 1, other values 0..2. Operate stage on a survey to apply settings. Probe or operate sensor on that survey to obtain ONE scalar response. Every input and trim is legal, including mission inputs; repeated use is unlimited but actions cost budget. Probe stage previews preparation without applying it; only operate applies. Configure doser with [a,b,c,d], then operate doser on seal to apply treatment. Probe doser previews without applying. Seal does not expose a sensor reading; surveys do not accept doser treatment. Re-preparation clears old readings. Configure alone never transforms a specimen. Carry the treated seal in array and finish. Failed finish reports only rejection and can be retried while budget remains; it never identifies a failing residual. Finish and all successful mutations cost one action. Observe, manifest, evidence and status are free. There is no reset.",
    }
