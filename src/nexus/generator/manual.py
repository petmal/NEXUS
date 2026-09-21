"""Player-facing description of the finite prototype causal grammar."""

FACILITY_MANUAL = """NEXUS TRANSFORMATION FACILITY — MACHINE LAW REFERENCE

Every transformation machine in this prototype obeys one deterministic conditional law.
The law is assembled from the finite grammar below. The selected law is hidden, but this
grammar is public.

CONDITION

The condition has one of these three forms:

1. (artifact shape is S) AND (facility phase has parity P)
2. (artifact shape is S) OR  (facility phase has parity P)
3. (artifact shape is NOT S) AND (facility phase has parity P)

S is one of: triangle, square, circle.
P is one of: even, odd.

TRUE-BRANCH TRANSFORMATION

If the condition is true, exactly one of these sequences is applied:

A. value := (value + 2) mod 11; toggle polarity; rotate clockwise 1 quarter-turn
B. value := (value + 3) mod 11; rotate clockwise 2 quarter-turns
C. value := (value * 2) mod 11; toggle polarity; rotate clockwise 3 quarter-turns
D. rotate clockwise 1 quarter-turn; toggle polarity

FALSE-BRANCH TRANSFORMATION

If the condition is false, exactly one of these sequences is applied:

A. value := (value * 3) mod 11; rotate clockwise 1 quarter-turn
B. value := (value + 1) mod 11; toggle polarity
C. rotate clockwise 2 quarter-turns
D. value := (value * 2) mod 11; toggle polarity; rotate clockwise 1 quarter-turn

ROTATION

Orientation cycles north -> east -> south -> west -> north.

EVIDENCE

measurements.csv contains prior experiments performed on the same machine law used in
this episode. Each row gives the facility phase and an artifact's input/output state.

The law does not depend on artifact pattern, room, turn number, or experiment history.
"""
