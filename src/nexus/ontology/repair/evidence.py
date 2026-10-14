"""Shared public contract, invariant across all selected hidden worlds."""

import json

from nexus.ontology.repair.schema import FAMILY


def files(spec):
    theory = {
        "family": FAMILY,
        "arithmetic": "Exact integers modulo7; every result is reduced to0..6.",
        "prior": "a,b,c,r independently range over0..6; d ranges over1,2,3. Every combination is admitted. They are fixed across all specimens in one episode.",
        "missing_relation": "f(z)=c+z, c+z*z, or c+(z*z)*z, with the same unknown c throughout. The selected exponent is d.",
        "reference": "A survey specimen on reference reports [a], regardless of its preparation.",
        "reader": {
            "unprepared": "null, independent of all hidden values",
            "mode_0": "After orientation[0,x] and charging: [b+r*(a-x)].",
            "mode_1": "After orientation[1,y] and charging: [f(0)+r*(b-y), f(2)+r*(b-y)].",
        },
        "seal_residuals": ["a-u", "b+a*u-v", "f(3)+b*v-w", "f(4)+f(3)*u*v-z"],
        "mission": "Apply doses[u,v,w,z] to the unique seal specimen; carry it into the array and finish. All four residuals must be0. Residuals are latent material responses, not exposed payload fields.",
        "feedback": "The seal material gives null on reference and reader for every dose. A failed finish gives only generic rejection; it is recoverable while actions remain. Successful finish is absorbing.",
        "preparation": "Stage overwrites a survey orientation and clears its charge. Coupler charges an oriented survey. Reader never changes preparation. Doser overwrites seal doses. Other material/apparatus pairings are insensitive: no hidden reading and no preparation/dose change.",
        "preview": "Probe previews the same public result as operate without committing it. Stage/coupler/doser previews disclose only public preparation/treatment fields, never a residual, hidden value or seal verdict.",
        "initial": "Stage and doser start unconfigured. Survey stocks are fresh, unoriented and uncharged. The unique seal has no applied dose. An unapplied seal is ineligible; residuals are evaluated only after a dose.",
        "controls": {
            "stage": "[mode,x] where mode0or1 and x0..6",
            "doser": "four selectors0..6; every vector is legal",
        },
    }
    manual = f"""SEALED ARRAY
The enclosure's exit accepts the unique specimen named seal only when its four
latent residuals are simultaneously zero. This is a concrete material condition;
submitting an equation or naming a hidden hypothesis cannot open the exit.
Read theory.json and map.json for the complete bounded artificial-law prior.

Take seal and take stock in {spec.stock_room}. A stock take returns a fresh survey
specimen ID. Carry both into {spec.mission_room}. Use the returned survey ID.
Configure stage with [mode,x], operate stage on a survey, then operate coupler
on it. Probe reader (or operate reader) to measure its prepared response.
Reference works on raw or prepared surveys. Every stage operation clears charge,
even when the selected orientation is unchanged. Configure alone changes no specimen.
Configure doser with [u,v,w,z], then operate doser on seal to apply that treatment.
Carry seal in the array and call finish. A new dose fully replaces an old dose;
there is no reset/replenish action. Survey stock and apparatus uses are unlimited.
All accepted actions except observe consume one action; invalid requests do not.
Free observations only report public preparation, cached readings and resources.
The phase register is constant in this stationary world. Respect the displayed
finite budget. It includes room for one additional failed complete seal attempt
(configure doser, operate seal, finish) after acquiring and carrying both materials
into the array. It does not promise recovery from arbitrary extra experiments.
All apparatus is usable immediately; no scientific result unlocks a control.
Finite enumeration is a valid inference method. Victory requires successful finish.
"""
    return {
        "manual.md": manual,
        "theory.json": json.dumps(theory, indent=2),
        "map.json": json.dumps(
            {
                "rooms": {spec.stock_room: "Material stores", spec.mission_room: "Sealed array"},
                "edges": []
                if spec.stock_room == spec.mission_room
                else [[spec.stock_room, spec.mission_room]],
            },
            indent=2,
        ),
    }
