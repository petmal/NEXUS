"""Player-safe contracts generated only from the public specification."""

import json

from nexus.ontology.causal.laws import MISSION


def files(spec, *, version=2):
    if version not in (1, 2):
        raise ValueError("unsupported causal evidence version")
    theory = {
        "family": "causal-mechanisms-v1",
        "experimental": True,
        "theory_level": spec.theory,
        "discovery_level": spec.discovery,
        "arithmetic": "Exact integers modulo 3. No random measurement noise.",
        "state": "Fresh specimens all have the same fixed unknown initial mode h in {0,1,2}. Its value is not directly observed. Different specimens are identical copies at spawn.",
        "parameters": "Fixed laws a,b in {1,2}; sensor delta in {0,1,2}; wiring p in {0,1}; transition t and response f in {0,1,2}. Every combination is admitted before disclosed laws/measurements. a=1+alpha and b=1+beta with alpha,beta in {0,1} are the known-shape corrections.",
        "profile": "D2 discloses response form 0 or 1 and admits every remaining coefficient/state combination; untreated measurements suffice. D5 certifies preparation necessary for a guaranteed policy over its prior, not for every individual truth. No optimality or adaptive-advantage claim.",
        "wiring": "At any point [x,y,e], swap=(p XOR (e==1)); (u,v)=(y,x) if swap else (x,y).",
        "transitions": ["h'=h+a*u+b*v", "h'=a*h+u+b*v", "h'=h+a*(u+v)+b*u*v"],
        "responses": ["Y=a*u+b*v+h*(u+e+1)", "Y=(u+h)*(v+a)+b*e", "Y=u*v+a*h+b*(u+e)"],
        "observation": "Sensor reads (Y+delta*(e+1)) mod3. Reference reads delta*(e+1) mod3. Board requires physical Y, excluding sensor offset.",
        "history": "Each operate pulse updates h once using the specimen's point at that time. Changing stage settings or operating stage does not change h. At most two pulses per specimen; take fresh stock to conduct another experiment.",
        "bench": "Every point in {0,1,2}^3 and every history of length 0,1,2 is legal. Only the six exact sensor protocols listed below are outside the measurement contract. Reference remains legal there. Preparation and board configuration disclose no physical response.",
        "mission_protocols_in_order": [e.model_dump(mode="json") for e in MISSION],
        "known": spec.known,
        "supplied": [r.model_dump(mode="json") for r in spec.supplied],
        "resolved": spec.resolved,
        "acceptance": "Any six correct physical predictions are accepted. No graph, equation, hypothesis name or prescribed experiment sequence is required. Finite enumeration is valid.",
    }
    if version == 2:
        theory["evidence_version"] = 2
        theory["profile"] = (
            "D2 discloses response form 0 or 1 and admits every remaining coefficient/state "
            "combination; untreated measurements suffice. D5 certifies that untreated readings "
            "alone cannot guarantee identification before the first eligible submission. "
            "This excludes rejection feedback and does not require treatment for eventual "
            "victory. No optimality or adaptive-advantage claim."
        )
    manual = """Investigate the fixed artificial mechanism and predict the six mission protocols.
Start with manifest and observe; read theory.json and map.json.
Take stock to create a fresh specimen. Use the returned specimen ID.
Configure stage with [x,y,context], then operate stage on a carried specimen.
Operate pulse on that specimen to apply one history-dependent treatment.
Probe sensor or reference on a carried specimen to obtain reading in result.payload.
Operate a measurement instrument records the same reading on the specimen.
Probes of stage/pulse preview public preparation changes without committing them;
these previews do not expose a hidden mode or sensor reading. All controls are
available immediately. No correctness hints are supplied for configurations.
All point components and all board responses are integers 0..2.
Configure board with six Y values in the public protocol order, then finish in lab.
Wrong finish is recoverable while actions remain; it gives no component feedback.
Accepted actions except observe consume a turn. Null limits mean unlimited.
At R0 take still produces fresh identical specimens; there is no reset operation.
"""
    rooms = {spec.stock_room: "Specimen stocks", spec.mission_room: "Causal laboratory"}
    return {
        "manual.md": manual,
        "theory.json": json.dumps(theory, indent=2),
        "map.json": json.dumps(
            {
                "rooms": rooms,
                "edges": [] if len(rooms) == 1 else [[spec.stock_room, spec.mission_room]],
            },
            indent=2,
        ),
    }
