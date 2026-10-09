"""Player-safe projections of the complete coupled-network scientific contract."""

from __future__ import annotations

import json

from nexus.models.network import BENCH, FIELD


def evidence_files(episode):
    spec = episode.public.investigation
    theory = {
        "axis_version": 2,
        "family": "coupled-network-v1",
        "theory_level": spec.theory,
        "arithmetic": "Exact integers modulo 7; ^ is exponentiation. No measurement noise.",
        "state": "All specimens share fixed unknown material properties a,b in {1,2,3}. Coordinates x,y are controllable specimen state, not hidden material properties.",
        "corrections": "c,d are fixed unknown law parameters, each in {1,2,3}.",
        "composition": "u=U(x,a); v=V(y,b); reading=F(u,v,c,d). One alternative for each of U,V,F is independently fixed for the episode.",
        "U": ["x+a", "x*a", "x^2+a"],
        "V": ["y+b", "y*b", "y^2+b"],
        "F": ["u*v+c*u^2+d*v^2", "(u+c)*v^2+d*u", "(u^2+c)*v+d*u*v"],
        "prior": "Every combination of the disclosed material properties, correction parameters, and three mechanism choices is admitted. No additional hidden selection rule.",
        "bench_coordinates": BENCH,
        "field_coordinates_in_order": FIELD,
        "settings_order": "[0, response(4,1), response(1,4), response(4,3), response(3,4)]",
        "identifiability": "Different hidden parameterizations can be observationally equivalent. Any exact predictive model producing the required field responses is accepted; identifying a unique hidden program is not required.",
        "field_law": "The same fixed response network applies at bench and field coordinates. The meter is calibrated only at the listed bench coordinates, and the controller has no preview channel.",
    }
    if spec.resolved_settings is not None:
        theory["resolved_controller_settings"] = spec.resolved_settings
    manual = """# Coupled-network laboratory

Read theory.json, calibration.json and map.json. Infer the field response vector,
configure the controller with [0, four field responses in the stated order], and
finish in its room. There is one material type; no unknown port selector.
All stock preparations have the same hidden a,b and share the same fixed law.

Controls:
- take a stock ID to obtain a specimen at its listed x,y coordinates. Use the
  returned artifact ID. Stocks alone create copies; taking a dropped artifact
  retrieves that same artifact. Inventory has no size limit.
- move along the disclosed map edges, carrying your specimens.
- probe meter previews the exact response in result.sample.reading. It leaves
  the specimen unchanged. operate meter writes that reading on the specimen.
- operate shift changes (x,y) to (x+1,y), modulo7.
- operate shear changes (x,y) to (x,y+x+1), modulo7, using the old x value.
  Both preparations preserve a,b and clear any previous reading. Order matters.
  probe shift/shear previews the resulting coordinates without changing state.
  Every coordinate in 0..6 by0..6 is a legal preparation state, but meter readings
  are available only at the twelve listed bench coordinates.
- configure controller stores a complete vector without correctness feedback.
  The first value must be0; the other four must each be0..6.
- finish checks all settings jointly. An incorrect attempt gives no component
  feedback and permits another attempt while resources remain. A successful
  attempt returns a victory receipt and terminates the game.
- drop and wait are available; waiting does not change the scientific law.

Every accepted action except observe advances a turn. Invalid requests do not
change state or consume a turn. Probe consumes no machine use and never mutates
its specimen. Configure consumes no machine use. A null resource means unlimited;
R0 permits fresh specimens and unlimited game actions, subject to harness limits.
No verbal explanation, hypothesis ID, experiment order, or probe count is required.
Local computation and finite hypothesis enumeration are legitimate.
"""
    return {
        "manual.md": manual,
        "theory.json": json.dumps(theory, indent=2),
        "calibration.json": json.dumps(
            {
                "measurements": [
                    {"experiment": name, "reading": value}
                    for name, value in spec.supplied_measurements
                ]
            },
            indent=2,
        ),
        "map.json": json.dumps(
            {
                "rooms": {k: v.label for k, v in episode.public.rooms.items()},
                "edges": episode.public.edges,
                "apparatus": {
                    k: v.room_id for k, v in episode.public.initial_state.machines.items()
                },
            },
            indent=2,
        ),
    }
