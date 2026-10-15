"""Scientific primitives, public play, private-state boundaries and exact replay."""

from itertools import product

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.dynamics.inference import initial_mask, policy_bound
from nexus.ontology.dynamics.laws import (
    MISSION,
    POINTS,
    WORLDS,
    experiments,
    physical,
    primitive,
    reading,
    targets,
)
from nexus.ontology.dynamics.policy import public_policy
from nexus.ontology.dynamics.schema import Experiment
from nexus.presentation import evidence_files
from nexus.protocol.session import Session


def episode(seed=128, *, control=False, planning=1):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="coupled-dynamics-v1",
        theory_level=0 if control else 3,
        discovery_level=0 if control else 5,
        planning_level=planning,
        resource_pressure=1,
        verifier_secret="test",
    )


def independent_step(a, b, p, t, f, h, k, point):
    x, y, e = point
    if bool(p) != (e == 1):
        x, y = y, x
    if t == 0:
        nh, nk = h + a * x + b * k, k + b * y + x * h
    elif t == 1:
        nh, nk = a * h + x * k + y, b * k + y * h + x
    else:
        nh, nk = h + a * x + k * y, k + b * y + h * x + x * y
    if f == 0:
        result = a * x + b * y + h * (x + e + 1) + k * (y + 1)
    elif f == 1:
        result = (x + h) * (y + k + a) + b * e
    else:
        result = x * y + a * h + b * k + h * k * (e + 1) + x * k
    return nh % 3, nk % 3, result % 3


def test_every_primitive_state_matches_independent_simultaneous_arithmetic():
    for a, b, p, t, f, h, k in product(
        (1, 2), (1, 2), range(2), range(3), range(3), range(3), range(3)
    ):
        for point in POINTS:
            assert primitive(a, b, p, t, f, h, k, point) == independent_step(
                a, b, p, t, f, h, k, point
            )
    # Inductively checked primitives also match an independent multi-pulse evaluator.
    for world in WORLDS:
        for experiment in MISSION:
            h, k = world.initial_h, world.initial_k
            for point in experiment.history:
                h, k, _ = independent_step(
                    world.a, world.b, world.wiring, world.transition, world.response, h, k, point
                )
            expected = independent_step(
                world.a,
                world.b,
                world.wiring,
                world.transition,
                world.response,
                h,
                k,
                experiment.point,
            )[2]
            assert physical(world, experiment) == expected


def test_complete_legal_experiment_space_and_private_state_projection():
    legal = experiments()
    assert len(legal) == 4674 and len(set(legal)) == 4674
    assert not set(MISSION) & set(legal)
    assert sum(e.instrument == "sensor" for e in legal) == 8 * (1 + 8 + 64 + 512) - 8
    for w in WORLDS[::31]:
        for history in ((), ((1, 1, 1),) * 3):
            for point in POINTS:
                assert reading(
                    w, Experiment(instrument="reference", history=history, point=point)
                ) == reading(w, Experiment(instrument="reference", point=(0, 0, point[2])))
    e = episode()
    public = e.public.model_dump_json()
    assert '"initial_h"' not in public and '"construction_seed"' not in public
    assert '"certificate"' not in public and '"world_index"' not in public
    other = episode(839)
    assert e.public.evidence_files == other.public.evidence_files


@pytest.mark.parametrize("seed", (128, 839, 1013, 649, 1509, 219))
def test_selected_worlds_win_with_public_information_and_replay(seed):
    e = PrivateEpisode.model_validate_json(episode(seed).model_dump_json())
    s = Session(e)
    result = public_policy(s, evidence_files(e.public))
    assert (
        result.victory_code
        and result.current_turn <= e.generation_metadata.guaranteed_policy_action_count
    )
    assert canonical_hash(replay(e, s.trace)) == canonical_hash(s.state)


@pytest.mark.parametrize("planning", (0, 1))
def test_resolved_control_requires_only_physical_execution(planning):
    e = episode(control=True, planning=planning)
    s = Session(e)
    result = public_policy(s, evidence_files(e.public))
    assert result.current_turn == 4 + planning and result.victory_code
    assert policy_bound(initial_mask(e.public.investigation.data())) == (0, 0)


def test_preview_configuration_and_insensitive_material_cannot_reveal_or_apply_treatment():
    e = episode(control=True, planning=0)
    s = Session(e)

    def act(a):
        return s.act(s.state.turn, a)

    assert act(TakeAction(artifact="seal")).ok
    assert act(ConfigureAction(machine="doser", settings=targets()[128])).ok
    preview = act(ProbeAction(machine="doser", artifact="seal"))
    assert preview.ok and s.state.artifacts["seal"].data().doses is None
    failure = act(FinishAction())
    assert not failure.victory_code and s.state.terminal_status.value == "active"
    measured = act(ProbeAction(machine="sensor", artifact="seal"))
    assert measured.ok and measured.events[0]["details"]["result"]["payload"]["reading"] is None
    assert act(OperateAction(machine="doser", artifact="seal")).ok
    assert act(FinishAction()).victory_code


def test_fourth_pulse_is_rejected_atomically_and_contract_tampering_fails():
    e = episode(planning=0)
    s = Session(e)
    result = s.act(0, TakeAction(artifact="stock"))
    stock = next(event["details"]["artifact"] for event in result.events if event["type"] == "take")
    for _ in range(3):
        assert s.act(s.state.turn, OperateAction(machine="pulse", artifact=stock)).ok
    before = canonical_hash(s.state)
    assert not s.act(s.state.turn, OperateAction(machine="pulse", artifact=stock)).ok
    assert canonical_hash(s.state) == before
    altered = e.model_copy(deep=True)
    altered.public.initial_state.resources.actions_remaining += 1
    assert not qualify_episode(altered).passed


@pytest.mark.slow
def test_every_admitted_dynamics_world_wins_and_replays():
    for seed in range(len(WORLDS)):
        e = episode(seed, planning=1)
        s = Session(e)
        result = public_policy(s, evidence_files(e.public))
        assert (
            result.victory_code
            and result.current_turn <= e.generation_metadata.guaranteed_policy_action_count
        ), seed
        assert canonical_hash(replay(e, s.trace)) == canonical_hash(s.state), seed
