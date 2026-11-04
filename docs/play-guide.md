# Your first visit to NEXUS

You are inside an artificial facility. Its exit seal opens only when you complete
the mission. The records tell you how to use the apparatus. Some worlds disclose
all of their laws; others leave questions for you to investigate.

The story is a setting for a precise puzzle. Real-world chemistry or physics
will not tell you the answer. Use this world's records and observations.

## Start with a guided visit

From the repository, run `uv run --frozen nexus demo`. You will see the evidence,
a short reference solution, and a victory receipt. This is an unscored tutorial.
Then run `uv run --frozen nexus demo --play` to try the same introductory setup.

The display shows your room, exits, objects you can see, objects you carry,
apparatus, and actions remaining. It does not show unseen objects elsewhere.

| Command | What it does |
|---|---|
| `look` | Show your current observation again |
| `mission` | Show the goal and list the evidence files |
| `evidence filename` | Read a listed file, such as `theory.json` |
| `help` | Show this world's actions and JSON examples |
| `quit` | Stop this local session |

These commands do not spend an environment action. File names and object IDs
vary by world: copy the identifiers displayed in your session.

## Take actions

Enter one JSON object per line. For example, if a visible artifact is named
`seal`, `{"type":"take","artifact":"seal"}` picks it up. Use
`{"type":"move","target":"room-id"}` with an exit listed in your observation.

Carried objects travel with you. To use an apparatus, you normally need to be in
its room and carry the object. `probe` previews a result without applying the
change; `operate` commits it. Both consume an action. Some families use additional
controls, such as `configure` or `spawn`; read `help` and the evidence first.

A turn is an accepted action, not a line of conversation or elapsed time.
`wait` also spends an action. A legal operation can consume resources even when
it changes nothing. Invalid requests do not partially change the world. Phase
is a separate world register, not a real-time clock.

When you believe the exact mission state is ready, enter `{"type":"finish"}`.
A successful finish produces the victory receipt. Merely reaching the right
physical state is not enough. A rejected finish still costs an action; whether
you can recover depends on the remaining resources and the world's rules.

## Read the records, then choose your next step

First locate the mission and its target. Check the layout, allowed controls,
resource budget, and any supplied laws. Decide what is already known and what an
experiment could resolve. Keep track of changes: in some worlds, progress on one
subgoal can disturb another. There are no secret story requirements beyond the
published mission and mechanics.

The local `play` process loads a private world so the engine can run it. Reading
that file or using `--debug-private` makes the session an unscored operator view.
Researchers should connect evaluated players through the restricted service.
Quitting does not save a resumable session; use an audit export to preserve its
history. [Evaluation guide](evaluation-guide.md).
