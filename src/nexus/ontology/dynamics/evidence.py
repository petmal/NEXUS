"""Player evidence contains the full prior, never the selected matrix stratum."""

import json

from nexus.ontology.dynamics.laws import MISSION
from nexus.ontology.dynamics.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "arithmetic": "Every expression is evaluated in exact integers modulo 3.",
        "prior": "a,b independently in {1,2}; initial h,k and sensor delta independently in {0,1,2}; wiring p in {0,1}; transition t and response f independently in {0,1,2}. All 1944 combinations are admitted. One fixed combination governs every specimen in this episode.",
        "state": "Fresh survey specimens share the same hidden initial pair (h,k). Their preparation history is public; h,k are never directly measured.",
        "controls": "A point [x,y,e] has each component in {0,1}. At most 3 pulses per survey. Configure stage then operate stage to set its point without changing h,k. Operate pulse applies one simultaneous transition using that point.",
        "routing": "swap=p XOR(e==1). Set(u,v)=(y,x) if swap else (x,y).",
        "transitions": [
            "(h',k')=(h+a*u+b*k, k+b*v+u*h)",
            "(h',k')=(a*h+u*k+v, b*k+v*h+u)",
            "(h',k')=(h+a*u+k*v, k+b*v+h*u+u*v)",
        ],
        "simultaneous": "Both right-hand expressions use the OLD h and k; never substitute h' while computing k'.",
        "responses": [
            "Y=a*u+b*v+h*(u+e+1)+k*(v+1)",
            "Y=(u+h)*(v+k+a)+b*e",
            "Y=u*v+a*h+b*k+h*k*(e+1)+u*k",
        ],
        "measurements": "Sensor reads Y+delta*(e+1). Reference reads delta*(e+1). Neither changes h,k. Sensor uses response f at the current point after all committed pulses.",
        "bench": "Every bit point and history of 0..3 bit points is legal, except sensor measurements of the eight exact mission protocols below. Reference remains legal there. This exclusion is part of the public bench contract.",
        "mission_protocols_in_order": [e.model_dump(mode="json") for e in MISSION],
        "mission": "The seal has eight latent residuals Y_i-dose_i, where Y_i is the physical response for mission protocol i starting at the common initial(h,k), excluding sensor offset. Configure doser with eight values 0..2, operate doser on seal, carry seal into array and finish. All residuals must be zero.",
        "seal": "The unique seal is insensitive to stage/pulse/sensor/reference: no preparation changes or readings. Doser overwrites all seal doses. Survey specimens are insensitive to doser. No preview or configuration exposes a residual or correctness verdict.",
        "feedback": "Failed finish is recoverable while budget remains and gives only generic rejection. Victory is absorbing. No experiment sequence or hypothesis name is required; any correct treatment wins. Finite hypothesis enumeration is allowed.",
        "resolved": spec.resolved,
        "resolved_meaning": "When non-null, resolved is the exact ordered dose vector supplied for the T0/D0 control. No scientific measurement is needed for that control.",
    }
    manual = """COUPLED ARRAY
The exit responds to a treated seal. Read theory.json and map.json for its exact
contract. Take seal and take stock; stock returns a fresh survey ID. Carry the
materials into array. Prepare a survey with configure stage [x,y,e], operate stage,
and operate pulse when a treatment is intended. Repeat with new stage points for
a longer history. A fresh specimen starts with an empty history and point [0,0,0].
Probe sensor/reference (or operate them) for a reading. Reusing a specimen retains
its entire pulse history. Take another stock specimen to begin a fresh experiment.
Probe previews never commit preparation or a dose; they expose only the same
public fields as the corresponding operation. All apparatus is available now.
Configure doser with eight ordered ternary values, then operate doser on seal.
Carry seal into array and finish. Configuration alone does not treat the seal.
All accepted actions except observe consume one action. Invalid requests do not.
Stock and apparatus uses are unlimited, but the total action allowance is finite.
The phase register is constant. Free observations expose only preparation,
cached readings and resources, never hidden components or residuals.
"""
    rooms = {spec.stock_room: "Material stores", spec.mission_room: "Coupled array"}
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
