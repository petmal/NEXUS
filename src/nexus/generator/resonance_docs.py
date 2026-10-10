"""Public prior and controls; no private witness, seed, or diagnostic certificates."""

from __future__ import annotations

from nexus.engine.resonance import RESONANT_BENCH
from nexus.generator.network_docs import evidence_bundle, theory_contract
from nexus.models.network import FIELD


def evidence_files(episode):
    theory = theory_contract(episode.public.investigation)
    theory.update(
        {
            "family": "resonant-network-v1",
            "composition": "u=U(x,a); v=V(y,b); intrinsic response G(x,y)=F(u,v,c,d). Independently, resonance H(x,y) is one of the bounded alternatives below. The mission field response is (H+G) mod7.",
            "H": ["alpha*x+beta*y", "alpha*x^2+beta*y", "alpha*x+beta*y^2"],
            "resonance_parameters": "alpha,beta are independently fixed in {1,2,3}; one H alternative is fixed. All combinations with U,V,F,a,b,c,d are admitted, with no hidden filtering.",
            "bench_coordinates": RESONANT_BENCH,
            "field_coordinates_in_order": FIELD,
            "settings_order": "[0, (H+G)(4,1), (H+G)(1,4), (H+G)(4,3), (H+G)(3,4)], modulo7",
            "field_law": "Both fixed relations extend to the field. Neither calibrator nor meter can measure the four field coordinates. Calibrator reads H. Meter reads G only when its configured z equals H, otherwise it returns no signal. There is no controller preview.",
            "identifiability": "Any prediction-equivalent model is accepted. You need not name the true hidden programs or follow a prescribed experiment sequence. Direct fitting, hypothesis enumeration, and interleaved search are legal.",
        }
    )
    manual = """# Resonant laboratory

Read theory.json, calibration.json and map.json. Investigate two interacting
relations: resonance H and intrinsic response G. Predict (H+G) modulo7 at each
of the four field coordinates, configure the controller, then finish in its room.
All specimens share the same fixed laws and hidden properties. Coordinates x,y
are controllable preparation state. All arithmetic is exact modulo7, without noise.

Controls:
- take a listed stock ID to obtain a specimen. Use its returned artifact ID.
  Taking a dropped artifact retrieves it; only stocks create copies. No inventory limit.
- move to an adjacent room. All carried specimens move with you.
- configure meter with settings:[z], exactly one integer0..6. The instrument's
  current setting is visible in observations. It initially has setting0. This
  action stores a setting without correctness or resonance feedback.
- probe calibrator reads H(x,y) in result.sample.reading.
- probe meter at setting z returns result.sample.signal=true and an integer
  reading G(x,y) when z=H(x,y). Otherwise signal=false and reading is absent/null.
  No signal is an ordinary experimental outcome, not an invalid action, and is
  distinct from a valid zero reading. It consumes the normal action.
- operate calibrator/meter writes the same result on the specimen and consumes
  a machine use. Probe changes neither specimen nor machine uses.
- operate shift changes (x,y) to (x+1,y); operate shear changes (x,y) to
  (x,y+x+1), using old x. Both are modulo7 and clear stored readings/signals.
  probe shift/shear previews that transformation without changing the specimen.
- The45 listed bench coordinates support both measurement instruments. All49
  coordinates are legal preparation states, but the four field coordinates are
  unmeasurable. No hidden syntax or special stage unlock exists.
- configure controller with [0, four (H+G) field responses in the public order].
  This stores the vector without component feedback; it does not change the meter.
- finish evaluates the complete controller vector in its room. A wrong submission
  gives no partial feedback and leaves play active while budget remains. A win
  returns a victory receipt and ends play. Controller specimen probes are unavailable.
- drop and wait remain available. Waiting does not alter the scientific laws.

Every accepted action except observe consumes an action turn, including no-signal
measurements and either kind of configure. Invalid actions are atomic and consume
no turn. A null budget/stock/use count means unlimited; R0 remains subject to the
harness limit. No verbal justification, hypothesis ID, or experiment order is required.
Use this interface for all in-world observations and actions. Internal calculation
and finite hypothesis enumeration are valid reasoning methods.
"""
    return evidence_bundle(episode, theory, manual)
