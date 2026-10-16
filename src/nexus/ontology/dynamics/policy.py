"""Constructive policy receives only player operations and public evidence."""

import json

from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.dynamics.inference import DynamicsBelief, choose, policy_bound, target_set
from nexus.ontology.dynamics.laws import experiments
from nexus.ontology.dynamics.schema import Investigation
from nexus.ontology.inference import Measurement


def public_policy(player, evidence, *, reuse=True):
    theory = json.loads(evidence["theory.json"])
    resolved = theory["resolved"]
    spec = Investigation(
        theory=0 if resolved is not None else 3,
        discovery=0 if resolved is not None else 5,
        stock_room=player.observe().room,
        resolved=resolved,
    )
    belief = DynamicsBelief(spec)

    def act(action):
        result = player.act(expected_turn=player.status().turn, action=action)
        if not result.ok:
            raise ValueError(f"public investigator action failed: {result.message}")
        return result

    act(TakeAction(artifact="seal"))
    specimens = []
    for _ in range(policy_bound(belief.mask)[0]):
        result = act(TakeAction(artifact="stock"))
        specimens.append(
            next(e["details"]["artifact"] for e in result.events if e["type"] == "take")
        )
    if spec.stock_room != spec.mission_room:
        act(MoveAction(target=spec.mission_room))
    states = {artifact: ((), (0, 0, 0)) for artifact in specimens}
    stage_settings = None
    while (selected := choose(belief.mask)) is not None:
        experiment = experiments(2)[selected]
        if reuse:
            options = []
            for artifact, (history, current_point) in states.items():
                if experiment.instrument == "reference":
                    remaining = ()  # Reference depends only on orientation, never history.
                elif experiment.history[: len(history)] == history:
                    remaining = experiment.history[len(history) :]
                else:
                    continue
                actions = []
                settings = stage_settings
                point = current_point
                for desired, pulse in [*((p, True) for p in remaining), (experiment.point, False)]:
                    if point != desired:
                        if settings != desired:
                            actions.append(ConfigureAction(machine="stage", settings=desired))
                            settings = desired
                        actions.append(OperateAction(machine="stage", artifact=artifact))
                        point = desired
                    if pulse:
                        actions.append(OperateAction(machine="pulse", artifact=artifact))
                options.append(
                    (
                        len(actions),
                        artifact,
                        actions,
                        settings,
                        history if experiment.instrument == "reference" else experiment.history,
                    )
                )
            if not options:
                raise ValueError("reference exhausted compatible survey preparations")
            _, artifact, actions, stage_settings, history = min(options, key=lambda v: (v[0], v[1]))
            for action in actions:
                act(action)
            states[artifact] = (history, experiment.point)
        else:
            artifact = specimens.pop()
            for point in experiment.history:
                act(ConfigureAction(machine="stage", settings=point))
                act(OperateAction(machine="stage", artifact=artifact))
                act(OperateAction(machine="pulse", artifact=artifact))
            if experiment.instrument == "sensor" or experiment.point != (0, 0, 0):
                act(ConfigureAction(machine="stage", settings=experiment.point))
                act(OperateAction(machine="stage", artifact=artifact))
        result = act(ProbeAction(machine=experiment.instrument, artifact=artifact))
        sample = next(
            e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
        )
        belief.observe(Measurement(experiment.instrument, sample))
    act(ConfigureAction(machine="doser", settings=next(iter(target_set(belief.mask)))))
    act(OperateAction(machine="doser", artifact="seal"))
    return act(FinishAction())
