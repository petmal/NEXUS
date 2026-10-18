"""Complete player contract; diagnostic proofs and selected hidden laws stay private."""

from __future__ import annotations

import json

from nexus.ontology.history.laws import PULSES


def files(spec):
    theory = {
        "specification": spec.model_dump(mode="json"),
        "field": "All values and arithmetic are modulo 3.",
        "state": "Physical registers are H,K,x,y. Initially all zero. Only x,y are visible. Internal coordinates h=a*H and k=b*K use fixed a,b independently in {1,2}.",
        "complete_prior": "Four independently composed gates F_i(u)=c_i*(1+(u+s_i)^2), with c_i in {1,2} and s_i in {0,1}. Every combination of four gates and a,b is possible: 1024 worlds. There is no hidden solvability filter, unlisted operation or noise.",
        "gate_encoding": "In a disclosed T0 law, selector q means c=1+floor(q/2), s=q mod 2. Procedure integers use pulse_order.",
        "pulse_order": PULSES,
        "updates": {
            "vek": "h <- h+F_0(k); other coordinates unchanged",
            "nol": "k <- k+F_1(h); other coordinates unchanged",
            "tor": "x <- x+F_2(h+k); THEN k <- k+x using NEW x",
            "sen": "y <- y+F_3(k+x); THEN h <- h+y using NEW y",
        },
        "readers": {
            "surface": "Return current x,y.",
            "h-scope": "On a COPY, set physical H=1 (therefore h=a), leave k,x,y unchanged, apply tor then sen exactly as above, return the COPY's x,y.",
            "k-scope": "On a COPY, set physical K=1 (therefore k=b), leave h,x,y unchanged, apply tor then sen exactly as above, return the COPY's x,y.",
        },
        "reading_scope": "visible always describes the specimen's actual x,y at its recorded history. reading describes the reader's result and may differ. Reader internals do not count toward the specimen's eight-pulse preparation limit. Probe or operate a reader never commits its temporary clamp or tor/sen updates.",
        "mission": "Carry seal in array with physical (H,K,x,y)=(1,2,1,2), then finish. Any preparation achieving this exact state wins. Matching visible x,y alone is insufficient. Finish returns success or binary rejection, no hidden register values. Rejections may be used as evidence and retried while budget remains.",
        "recovery": "Operate anneal restores all four specimen registers to zero and clears its history and cached reading. This costs one action, preserves the world's laws and all previous evidence, and is available throughout. It is not a new episode.",
    }
    return {
        "facility.txt": "You are trapped in a coupled array. Four pulse apparatuses alter a seal's internal and visible registers. Later pulses can disturb properties established earlier. Identical stock specimens support experiments under the same fixed laws. Infer a workable procedure, construct the seal, carry it in array and finish. Names have no outside physical meaning. Read theory.json and apparatus.txt.",
        "theory.json": json.dumps(theory, sort_keys=True, separators=(",", ":")),
        "apparatus.txt": "Take seal and/or take stock to receive a reusable survey specimen ID. Move to array if needed. All apparatuses are in array; none accepts configure. Operate vek, nol, tor or sen on a carried specimen to commit one pulse. The response supplies its full public pulse history and current visible x,y, but no H or K. At most eight pulses may be committed since the last anneal. Probe a pulse returns the one-step counterfactual result without changing the actual specimen or its history. It cannot chain uncommitted previews. Probe or operate surface, h-scope or k-scope to obtain reading; operate only caches that reading. Operate anneal recovers a specimen, including seal, to fresh zero state. Stock and machine use are unlimited; actions remain budgeted unless the manifest says unlimited. Take, move, operate, probe, wait and finish cost one action. Manifest, evidence, observe and status are free. Invalid actions do not consume actions or alter state. Finish may be retried after rejection. A successful finish ends the episode and returns the actual victory receipt. There is no session reset.",
    }
