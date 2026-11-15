"""Executable public-only evidence policy and reusable physical construction plan."""


from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.assembly.inference import Belief
from nexus.ontology.assembly.laws import BUILDS, QUERIES, accepted
from nexus.ontology.assembly.schema import Investigation
from nexus.ontology.inference import Measurement


def construction(build, artifact="carrier"):
    """Reach any build from ANY prior component state in two preparations.

    First B is set to A-B. Preparing C then rotates B to A and overwrites
    C, so the temporary rotation of an old C has no effect on the final state.
    """
    s, a, t, b, h = build
    return (
        ConfigureAction(machine="forge", settings=(0, s, (a - b) % 3)),
        OperateAction(machine="forge", artifact=artifact),
        ConfigureAction(machine="forge", settings=(1, t, b)),
        OperateAction(machine="forge", artifact=artifact),
        ConfigureAction(machine="assembler", settings=(h,)),
        OperateAction(machine="assembler", artifact=artifact),
    )


def omniscient_construction(world):
    """Shortest physical witness, independently checked against the full state BFS.

    Only the private CLI solver uses truth. Public investigation uses construction
    after finding a common build. Skip unchanged settings and consider every
    behaviorally accepted phase assignment, rather than a preferred spelling.
    """
    options = []
    for build in BUILDS:
        if not accepted(world, build):
            continue
        settings = {"forge": (0, 1, 0), "assembler": (0,)}
        plan = []
        for action in construction(build):
            if isinstance(action, ConfigureAction):
                if settings[action.machine] == action.settings:
                    continue
                settings[action.machine] = action.settings
            plan.append(action)
        options.append(tuple(plan))
    return min(options, key=len)


def public_policy(player, evidence):
    from nexus.ontology.player_records import specification

    spec = specification(Investigation, evidence, family="joint-assembly-v1")
    posterior = Belief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"assembly public policy failed: {result.message}")
        return result

    if not any(a.id == "carrier" for a in player.observe().carried_artifacts):
        act(TakeAction(artifact="carrier"))
    if player.observe().room != "workshop":
        act(MoveAction(target="workshop"))
    while (q := posterior.choose_query()) is not None:
        act(ConfigureAction(machine="reader", settings=QUERIES[q]))
        result = act(ProbeAction(machine="reader", artifact="carrier"))
        reading = next(
            e["details"]["result"]["payload"]["reading"]
            for e in result.events
            if "result" in e["details"]
        )
        posterior.observe(Measurement("reader", reading))
    for action in construction(posterior.common_decisions()[0]):
        act(action)
    return act(FinishAction())
