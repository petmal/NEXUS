# The Sealed Facility

You are inside NEXUS, an automated facility whose makers are unknown. Its exit
interlock is closed. A console translates the surviving labels and records into
readable instructions, and offers clearance when you complete a local mission.
The machinery responds reliably, but the records may leave parts of its behavior
for you to discover.

One visit might ask you to calibrate a controller. Another might require a
replacement cartridge, treatment of a seal specimen, or coordinated changes to
several registers. The available apparatus lets you work on the problem; the
exit interlock checks the completed result. Knowing whether a result is acceptable
does not make the interlock a source of explanations or solution hints. Its exact
feedback is stated in the mission's records.

Each episode is a separate visit, not a chapter in a campaign. The facility's
origin supplies atmosphere; discovering its makers is not an extra objective.
There are no unlisted characters to question, secret passwords to guess, or
story objects to find. The published mission is the whole success condition.

## Read the names as labels

The console's terminology describes artificial mechanisms. A familiar word does
not promise familiar physics, and an unfamiliar word is not a language puzzle.
The world tells you what its terms mean. Copy the exact IDs when issuing actions.

| Term | Meaning in play |
|---|---|
| Sector | A room. Use its displayed ID for movement. |
| Apparatus | A machine or instrument with listed controls. |
| Artifact / specimen | An object you can manipulate / an object used for experiments. |
| Stock | A source of specimens, subject to the displayed limits. |
| Array / lattice | A work area or group of apparatus / a system of connected elements. Neither word implies an unlisted device or route. |
| Exit seal / interlock | The lock that grants clearance after a successful mission. |
| `seal`, `seal-i`, `carrier` | Object IDs used in some missions. These are portable parts, not the exit door. A carrier holds a constructed device. |
| Cartridge / compensator | A programmed component / a device or treatment that supplies the correction required by the mission. |
| Register / excitation / residual | A state value / an input setting / the mismatch defined by the local records. |
| Phase, charge, orientation, pulse | Local state labels or controls. Their definitions come from this world's records. |

Not every visit uses every term. The labels explain how to read the interface;
they do not identify a hidden law, a useful experiment, or the correct settings.

## Time, limits and the ending

The action allowance is an authorization budget for commands, not an oxygen supply
or a real-time countdown. You can read and think without spending it. An accepted
action can cost an action even when it makes no visible progress. Device uses and
stock quantities can have separate limits. A `null` allowance means unlimited.
Phase changes follow the action contract, not elapsed time.

When the mission state is ready, invoke `finish`. A successful check grants exit
clearance and returns the victory receipt. That is the ending: there is no extra
door-opening or escape action. A rejected finish follows the stated world policy;
some permit another attempt while others end the session. Exhaustion or another
unsuccessful ending leaves clearance ungranted, without an additional story penalty.
`quit` stops the local program; it is not a victory.

See the [play guide](play-guide.md) for commands and a guided first visit.

## Presentation and reproducibility

New worlds use `sealed-facility-v5`. Their records describe this run’s instruments and disclosures. The same introduction and terminology reach
human and model players through the manifest and the listed manual or `facility.txt`.
The presentation uses only public information. It does not change identifiers,
numeric values, formal laws, action costs, goals or acceptance rules. Canonical
evidence remains available to qualification; player-facing exports use the same
rendering as the service and local interface.

Saved `sealed-facility-v1`, `sealed-facility-v2`, `sealed-facility-v3` and `sealed-facility-v4` worlds retain their original text. Worlds without a
presentation version retain their canonical text. For an old/new wording control,
use `generate_episode(..., presentation_version="sealed-facility-v1")`; use `None`
for canonical presentation. Record the version and source digest when comparing
runs. The standalone categorical prototype also uses the shared setting.

Keep story writing separate from hidden world truth. Do not add labels based on
a selected hidden rule, optimal plan, future state or qualification result. A
disclosed-law control must not be described as having an unknown mechanism.
