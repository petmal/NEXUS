"""Independent grammar arithmetic, operational ambiguity and live conformance."""

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
from nexus.ontology.compositional import runtime
from nexus.ontology.compositional.inference import Belief, audit, reading_bound
from nexus.ontology.compositional.laws import (
    MISSION,
    QUERIES,
    REPAIRS,
    accepted,
    population,
    reading,
)
from nexus.ontology.compositional.policy import public_policy
from nexus.protocol.session import Session


def episode(seed=438, planning=0, control=False):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="compositional-repair-v1",
        theory_level=0 if control else 3,
        discovery_level=0 if control else 5,
        planning_level=planning,
        resource_pressure=1,
        verifier_secret="test",
    )


def independent(world, mode, point, trims):
    topology, f, g, h, changed, replacement = world
    ops = [lambda x, y: x + y, lambda x, y: x - y, lambda x, y: x * y, lambda x, y: x**2 + y]
    selected = [f, g, h]
    if mode == 1:
        selected[changed] = replacement
    x, y, z = point
    a, b, c, d = trims
    first = (ops[selected[0]](x, y) + a) % 3
    second = (ops[selected[1]](y if topology == 1 else first, z) + b) % 3
    last = ops[selected[2]](second, x) if topology == 0 else ops[selected[2]](first, second)
    return (last + c + mode * d) % 3


def test_complete_disclosed_support_and_independent_acceptance():
    worlds = population()
    assert len(worlds) == 615
    assert len({w for w, _ in worlds}) == 615
    assert {w.topology for w, _ in worlds} == {0, 1, 2}
    for world, wins in worlds:
        independent_wins = 0
        for index, dose in enumerate(REPAIRS):
            success = all(independent(world, mode, point, dose) == 0 for mode, point in MISSION)
            assert accepted(world, dose) == success
            if success:
                independent_wins |= 1 << index
        assert wins == independent_wins
    independent_support = []
    for world in product(range(3), range(4), range(4), range(4), range(3), range(4)):
        if world[5] == world[1 + world[4]]:
            continue
        if any(
            all(independent(world, mode, point, dose) == 0 for mode, point in MISSION)
            for dose in REPAIRS
        ):
            independent_support.append(world)
    assert [tuple(world) for world, _ in worlds] == independent_support
    assert not audit().common(audit().full)
    assert reading_bound(audit().full) == 7


@pytest.mark.slow
def test_all_raw_queries_normalize_without_losing_information():
    for world, _ in population():
        for mode, point, (a, b) in QUERIES:
            baseline = independent(world, mode, point, (a, b, 0, 0))
            for c, d in product(range(3), repeat=2):
                settings = (mode, *point, a, b, c, d)
                result = reading(world, settings)
                assert result == independent(world, mode, point, (a, b, c, d))
                assert (result - c - mode * d) % 3 == baseline


def test_exact_shortcut_ceiling_and_common_repair_not_signature_count():
    data = audit()
    assert data.success_mass(0) == 41
    assert data.success_mass(1) == 95
    # Distinct winning sets may share a repair; such a belief IS resolved.
    pair = next(
        (1 << i) | (1 << j)
        for i, (_, a) in enumerate(population())
        for j, (_, b) in enumerate(population())
        if a != b and a & b
    )
    belief = Belief(episode().public.investigation.data())
    belief.mask = pair
    assert belief.counts()[1] == 2 and belief.common_decisions()
    repair = REPAIRS[belief.common_decisions()[0]]
    assert belief.supports(repair)
    belief.exclude_target(repair)
    assert belief.mask == 0


@pytest.mark.slow
def test_two_query_and_arbitrary_order_two_guess_ceilings():
    assert audit().success_mass(2) == 202
    assert audit().success_mass(1, 2) == 163


def test_intervention_and_single_context_obstructions_are_distinct():
    data = audit()
    for index in (438, 463, 493, 496, 541, 542):
        passive = data.closure(index, [i for i, q in enumerate(QUERIES) if q[2] == (0, 0)])
        assert not data.common(passive)
        assert passive.bit_count() == 2
        assert data.positive_reading_lower(index) == 3
    assert data.positive_reading_lower(250) == 2
    # This deliberately weak case is a legitimate control, not "deep" by label.
    assert data.common(data.closure(0, [i for i, q in enumerate(QUERIES) if q[2] == (0, 0)]))


@pytest.mark.parametrize("seed", (0, 250, 438, 463, 493, 496, 541, 542))
def test_public_witness_live_replay_and_metrics(seed):
    e = episode(seed, planning=1)
    s = Session(e)
    result = public_policy(s, e.public.evidence_files)
    assert result.victory_code and result.current_turn <= 27
    assert canonical_hash(replay(e, s.trace)) == canonical_hash(s.state)
    metrics = result.model_dump(mode="json")["performance"]
    assert metrics["version"] == "mission-performance-v2"
    assert metrics["first_submission_supported_by_evidence"]
    assert metrics["common_repairs_before_first_submission"] >= 1


def test_preview_invalid_actions_and_noncanonical_repairs():
    index = next(i for i, (_, wins) in enumerate(population()) if wins.bit_count() > 1)
    e = episode(index)
    s = Session(e)

    def act(action):
        return s.act(s.state.turn, action)

    assert act(TakeAction(artifact="seal")).ok
    alternatives = [dose for dose in REPAIRS if accepted(runtime.world_for(e), dose)]
    dose = alternatives[-1]
    assert dose != runtime.expected(e)
    assert act(ConfigureAction(machine="doser", settings=dose)).ok
    assert act(ProbeAction(machine="doser", artifact="seal")).ok
    assert s.state.artifacts["seal"].data().doses is None
    assert not act(FinishAction()).victory_code
    assert (
        act(ProbeAction(machine="sensor", artifact="seal")).events[0]["details"]["result"][
            "payload"
        ]["reading"]
        is None
    )
    before = canonical_hash(s.state)
    assert not act(ConfigureAction(machine="stage", settings=(2,) * 8)).ok
    assert canonical_hash(s.state) == before
    assert act(OperateAction(machine="doser", artifact="seal")).ok
    assert act(FinishAction()).victory_code


@pytest.mark.parametrize("planning", (0, 1))
def test_control_and_compiled_contract(planning):
    e = episode(planning=planning, control=True)
    assert public_policy(Session(e), e.public.evidence_files).current_turn == 4 + planning
    altered = e.model_copy(deep=True)
    altered.public.initial_state.resources.actions_remaining += 1
    assert not qualify_episode(altered).passed


@pytest.mark.slow
def test_every_world_live_wins_replays_and_accepts_its_whole_repair_set():
    for seed, (world, wins) in enumerate(population()):
        e = episode(seed, planning=1)
        s = Session(e)
        result = public_policy(s, e.public.evidence_files)
        assert result.victory_code and result.current_turn <= 27, seed
        assert canonical_hash(replay(e, s.trace)) == canonical_hash(s.state), seed
        # Acceptance seam is exercised for every legal physical treatment.
        for index, doses in enumerate(REPAIRS):
            artifact = s.state.artifacts["seal"]
            artifact.payload = (
                artifact.data().model_copy(update={"doses": doses}).model_dump(mode="json")
            )
            runtime.assess_mission(e, s.state)
            assert s.state.mission_accepted == bool(wins >> index & 1)


def test_ineligible_finish_does_not_eliminate_correct_physical_treatment():
    from nexus.models.actions import DropAction, MoveAction
    from nexus.protocol.session import ActionResponse

    e = episode(planning=1)
    s = Session(e)

    def act(action):
        return s.act(s.state.turn, action)

    for action in (
        TakeAction(artifact="seal"),
        MoveAction(target="array"),
        ConfigureAction(machine="doser", settings=runtime.expected(e)),
        OperateAction(machine="doser", artifact="seal"),
        DropAction(artifact="seal"),
    ):
        assert act(action).ok
    assert not act(FinishAction()).victory_code
    assert act(TakeAction(artifact="seal")).ok
    result = act(FinishAction())
    assert result.victory_code
    metrics = result.model_dump(mode="json")["performance"]
    assert metrics["failed_finishes"] == 1
    assert metrics["target_classes_before_first_submission"] == 216
    assert metrics["first_submission_supported_by_evidence"] is False
    assert ActionResponse.model_validate_json(result.model_dump_json()) == result
    assert canonical_hash(replay(e, s.trace)) == canonical_hash(s.state)


def test_offset_operate_sensor_after_eligible_failed_repair():
    from nexus.ontology.inference import Measurement

    e = episode()
    s = Session(e)

    def act(action):
        return s.act(s.state.turn, action)

    act(TakeAction(artifact="seal"))
    result = act(TakeAction(artifact="stock"))
    survey = next(v["details"]["artifact"] for v in result.events if v["type"] == "take")
    wrong = next(d for d in REPAIRS if not accepted(runtime.world_for(e), d))
    act(ConfigureAction(machine="doser", settings=wrong))
    act(OperateAction(machine="doser", artifact="seal"))
    assert not act(FinishAction()).victory_code
    settings = (1, 2, 2, 1, 2, 1, 2, 2)
    act(ConfigureAction(machine="stage", settings=settings))
    act(OperateAction(machine="stage", artifact=survey))
    result = act(OperateAction(machine="sensor", artifact=survey))
    payload = result.events[0]["details"]["result"]["payload"]
    belief = Belief(e.public.investigation.data())
    belief.exclude_target(wrong)
    belief.observe(Measurement("sensor", payload))
    oracle = sum(
        1 << i
        for i, (w, _) in enumerate(population())
        if not accepted(w, wrong)
        and independent(w, 1, settings[1:4], settings[4:]) == payload["reading"]
    )
    assert belief.mask == oracle
    _, metrics = s.finalize_attempt()
    assert metrics.measurements_used == 1 and metrics.failed_finishes == 1


def test_control_posterior_matches_disclosed_canonical_sampling():
    e = episode(control=True)
    spec = e.public.investigation.data()
    belief = Belief(spec)
    expected = sum(
        1 << i
        for i, (w, _) in enumerate(population())
        if next(d for d in REPAIRS if accepted(w, d)) == spec.resolved
    )
    assert belief.mask == expected and belief.supports(spec.resolved)
