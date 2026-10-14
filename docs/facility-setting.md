# The Sealed Facility

Current generated NEXUS episodes use presentation `sealed-facility-v1` across
legacy artifact missions and all scientific ontologies. A player is confined in
an artificial facility and must open its exit seal by producing the exact stated
mission state and successfully invoking `finish`. Records describe the local
laws and controls; experiments supply evidence where those records are insufficient.

| Public term | Meaning |
|---|---|
| Sector | A room; its existing identifier remains the movement argument. |
| Apparatus | An existing machine or instrument, with its documented controls. |
| Artifact / specimen | The existing manipulable object, with its exact public fields. |
| Seal | The mission's acceptance condition; it adds no hidden condition or action. |
| Turn | A committed environment action under the existing action contract. |
| Phase | The existing separate phase register; it is not wall time or a new deadline. |
| Victory receipt | The actual code returned after successful `finish`. |

The premise intentionally supplies no real-world scientific analogies or hints
about which experiment is useful. Identifiers, numeric values, law grammar,
finite/unlimited resources, and goal predicates retain their exact meanings.
Existing ontology-specific instructions remain part of the records.

Presentation is a public-only renderer, separate from scientific execution.
Manifest, observation, HTTP evidence, CLI and exported attachments share it.
Canonical evidence remains unchanged for validation. Historical serialized
worlds lacking a presentation version retain their original text. The central
`generate_episode(..., presentation_version=None)` option reproduces historical
presentation; it does not alter the scientific seed or action semantics.

Scientific generators below the central factory remain canonical compilation
functions. Current player entry points use the factory; the standalone categorical
PoC also selects the shared presentation. No difficulty guarantee follows from
the story or from a historical D/T label.
