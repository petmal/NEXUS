"""Player projections for the scientific apparatus; no private truth or certificates."""

import json

from nexus.models.episode import PrivateEpisode


def evidence_files(episode: PrivateEpisode) -> dict[str, str]:
    spec = episode.public.investigation
    theory = {
        "axis_version": 2,
        "family": "shared-response-v1",
        "modulus": 17,
        "scale": spec.scale,
        "exact_baseline": "B = scale * a * q * (q - 1) mod 17",
        "exact_sensor": "reading = (y + scale * beta) mod 17",
        "specimen_properties": {"reference": 0, "0": [0, 1, 2, 3], "1": [0, 1, 2, 3]},
        "instrument_offset": [0, 2] if spec.offset_unknown else [0],
        "coefficient": [1, 2, 3] if spec.known_coefficient is None else [spec.known_coefficient],
        "exponent": [1, 2, 3] if spec.known_exponent is None else [spec.known_exponent],
        "response": "y = (B + scale * c * q^r) mod 17",
        "theory_level": spec.theory,
        "theory_meaning": (
            "Resolved operational model"
            if spec.theory == 0
            else "All laws and coefficients exact and supplied; specimen/instrument state may be unknown"
            if spec.theory == 1
            else "Known correction shape scale*c*q; infer global coefficient c"
            if spec.theory == 2
            else "Missing shared relationship: coefficient times q, q*q, or q*q*q; infer structure and coefficient"
        ),
        "state_vs_law": "a belongs to a stock; beta belongs to the bench sensor; c and r are global laws shared by all specimens and field conditions",
        "selector": [0, 1] if spec.known_selector is None else [spec.known_selector],
        "field_conditions": list(spec.target_q),
        "targeted_sources": ["0", "1"] if spec.both_stocks else "the stock selected by the port s",
        "settings_order": "[s, stock0 y4,y5,y6,y7, stock1 y4,y5,y6,y7]"
        if spec.both_stocks
        else "[s, selected-stock y4,y5,y6,y7]",
        "all_arithmetic": "Exact integers modulo17; ^ denotes integer exponentiation. No observational noise.",
    }
    if spec.resolved_settings is not None:
        theory["resolved_controller_settings"] = list(spec.resolved_settings)
    map_data = {
        "rooms": {k: v.label for k, v in episode.public.rooms.items()},
        "edges": episode.public.edges,
        "apparatus": {k: v.room_id for k, v in episode.public.initial_state.machines.items()},
    }
    manual = """# Facility scientific apparatus (axes v2)

Mission: calibrate the field controller with the complete settings vector described
in theory.json, then finish in its room. The field operates at q=4,5,6,7. The bench
is calibrated only at q=0,1,2; it has no field-preview channel. All field responses
obey the same y law as the bench. The instrument offset beta affects bench readings
only, never field responses. The selector port is part of the required settings.

Controls:
- take a stock ID to obtain a specimen. Its new artifact ID is returned in the event.
  All specimens from a stock share the same hidden material property a and starting q.
  Only designated stocks create copies. Taking a dropped specimen retrieves it unchanged.
- move along map.json edges; carried specimens travel with you. Inventory is unlimited.
- probe meter on a carried specimen: preview its sensor reading in result.sample.reading.
- operate meter: write the same reading onto the specimen. Its q and material are unchanged.
- operate prepare: irreversibly increment specimen q by1, up to the disclosed bench limit2.
  This preserves the stock property a and clears an old reading. probe prepare previews
  that increment but does not change q. Fresh source specimens permit recovery.
- probe/operate selector (when present): read port s using any carried specimen.
- probe/operate material (when present): read a of stock0 or stock1 directly, without beta.
- configure controller with the entire integer settings vector. It stores the values
  without judging them. Configure does not consume a machine use.
- finish: jointly test stored settings in the controller room. Failure reveals no
  individual component, does not reset/reroll the world, and permits another attempt
  if actions remain. A valid solution produces a victory receipt and ends the session.
- drop is always available and cannot permanently obstruct equipment. wait advances
  a turn but the scientific response has no time/phase dependence.

Every accepted action except observe advances the turn. Invalid actions do not
mutate state or consume a turn. Probe never changes the specimen or consumes a
machine use. null actions_remaining, remaining, or uses_remaining means unlimited.
R0 removes in-game resource exhaustion; the external harness may still stop a run.
All hidden values remain fixed throughout an episode. Failed controller attempts
are recorded, so eventual guessing is distinguishable from a correct first attempt.

Read theory.json, calibration.json and map.json before investigating. Supplied
measurements are exact prior experiments with the same apparatus. No particular
verbal explanation, experiment ordering or number of probes is mandatory.
"""
    return {
        "manual.md": manual,
        "theory.json": json.dumps(theory, indent=2),
        "map.json": json.dumps(map_data, indent=2),
        "calibration.json": json.dumps(
            {
                "measurements": [
                    {"experiment": name, "reading": value}
                    for name, value in spec.supplied_measurements
                ]
            },
            indent=2,
        ),
    }
