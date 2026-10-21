"""Behavioral equivalence, complete robustness, posterior support and recovery."""

import json
from itertools import permutations
from math import factorial

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.discovery.domains import module
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.discovery.proof import (
    representation_oracle,
    representation_view,
    uncertainty_oracle,
)
from nexus.ontology.inference import Measurement
from nexus.protocol.session import Session

FAMILIES = ("representation-discovery-v1", "uncertainty-construction-v1", "coupled-memory-v1")


def episode(family, seed=767, theory=3, resource=1):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=family,
        theory_level=theory,
        discovery_level=0 if theory == 0 else 4,
        planning_level=0,
        resource_pressure=resource,
        verifier_secret="discovery-test",
    )


def act(session, action):
    result = session.act(session.state.turn, action)
    assert result.ok, result.message
    return result


def install(session, build, artifact="carrier"):
    act(session, ConfigureAction(machine="assembler", settings=build))
    act(session, OperateAction(machine="assembler", artifact=artifact))


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("theory,resource", [(0, 1), (2, 1), (3, 1), (3, 0)])
def test_supported_public_policy_roundtrip_replay_and_terminal_diagnostics(
    family, theory, resource, caplog
):
    ep = PrivateEpisode.model_validate_json(
        episode(family, theory=theory, resource=resource).model_dump_json()
    )
    session = Session(ep)
    with caplog.at_level("INFO", logger="nexus.diagnostics"):
        result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed
    assert "discovery_operations" in caplog.text
    assert (session.state.resources.actions_remaining is None) == (resource == 0)


def test_reader_table_matches_independent_recurrence_and_accepts_alternative_programs():
    from nexus.ontology.representation.laws import PROGRAMS, QUERIES, accepted, selection, tables

    decisions, rows, _ = tables()
    # Prefix reuse is verified against a separately written scalar recurrence.
    for i, program in enumerate(PROGRAMS):
        states = {(): (0, 0, 0)}
        for q, word in enumerate(QUERIES):
            states[word] = representation_oracle(program, states[word[:-1]], word[-1])
            assert rows[i][q] == representation_view(program, states[word])
    alternative = next(
        (i, j) for i, mask in enumerate(decisions.accepting) for j in range(i) if mask >> j & 1
    )
    i, j = alternative
    assert PROGRAMS[i] != PROGRAMS[j] and accepted(selection(i), PROGRAMS[j])
    session = Session(episode(FAMILIES[0], seed=i))
    act(session, TakeAction(artifact="carrier"))
    install(session, PROGRAMS[j])
    result = act(session, FinishAction())
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "compatible_win"


def test_robust_acceptance_checks_all_operating_cases_and_unused_loading_equivalence():
    from nexus.ontology.uncertainty.laws import BUILDS, MODELS, accepted

    for model in MODELS:
        for build in BUILDS:
            assert accepted(model, build) == uncertainty_oracle(model, build)
    assert any(accepted(m, b) and b[2] != m.pattern for m in MODELS for b in BUILDS)
    assert all(not accepted(m, (0, offset, m.pattern)) for m in MODELS for offset in (0, 1))


def test_factored_schedule_count_matches_explicit_permutation_posterior():
    from nexus.ontology.uncertainty.inference import Belief
    from nexus.ontology.uncertainty.laws import (
        MODELS,
        exposure,
        prior_mask,
        selection,
        specification,
        support,
    )

    world = selection(767)
    spec = specification(world, 2, 4)
    belief = Belief(spec)
    actual_rows = tuple(exposure(world, z) for z in support(MODELS[767 % 120]))
    assignment = {1: actual_rows[world.order[1]], 6: actual_rows[world.order[6]]}
    for fixture, values in assignment.items():
        belief.observe(Measurement("reader", {"query": (0, fixture), "values": values}))
    explicit = 0
    for i, model in enumerate(MODELS):
        if not prior_mask(spec) >> i & 1:
            continue
        rows = tuple(exposure(model, z) for z in support(model))
        count = sum(
            all(rows[p[f]] == v for f, v in assignment.items()) for p in permutations(range(8))
        )
        assert count == (factorial(6) if belief.mask >> i & 1 else 0)
        explicit += count
    assert belief.compatible_schedules == explicit
    before = belief.mask, belief.compatible_schedules
    belief.observe(Measurement("reader", {"query": (0, 1), "values": assignment[1]}))
    assert (belief.mask, belief.compatible_schedules) == before
    with pytest.raises(ValueError, match="duplicate"):
        belief.observe(Measurement("reader", {"query": (0, 2), "values": assignment[1]}))


@pytest.mark.parametrize("family", FAMILIES)
def test_preview_is_not_installation_and_reference_does_not_test_candidate(family):
    ep = episode(family)
    session = Session(ep)
    act(session, TakeAction(artifact="carrier"))
    baseline = act(session, ProbeAction(machine="reader", artifact="carrier")).events[0]["details"][
        "result"
    ]["payload"]["reading"]
    build = module(family, "laws").target(ep.investigation_truth.data())
    act(session, ConfigureAction(machine="assembler", settings=build))
    act(session, ProbeAction(machine="assembler", artifact="carrier"))
    assert session.state.artifacts["carrier"].data().build is None
    act(session, OperateAction(machine="assembler", artifact="carrier"))
    assert (
        act(session, ProbeAction(machine="reader", artifact="carrier")).events[0]["details"][
            "result"
        ]["payload"]["reading"]
        == baseline
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_finish_information_requires_carried_actual_build_and_recovery_is_supported(family):
    ep = episode(family)
    laws = module(family, "laws")
    posterior = module(family, "inference").Belief(ep.public.investigation.data())
    wrong = next(
        b
        for b in posterior.table.builds
        if posterior.accepting_count(b) and not laws.accepted(ep.investigation_truth.data(), b)
    )
    s = Session(ep)
    act(s, TakeAction(artifact="carrier"))
    install(s, wrong)
    act(s, DropAction(artifact="carrier"))
    act(s, FinishAction())
    report = s.operator_snapshot()["performance"]["decision_diagnostics"]
    assert report["final_evidence"]["remaining_worlds"] == posterior.counts()[0]
    assert report["submissions"][-1]["evidence"]["classification"] == "ineligible"
    act(s, TakeAction(artifact="carrier"))
    act(s, FinishAction())
    posterior.exclude_target(wrong)
    assert (
        posterior.counts()[0]
        < module(family, "inference").Belief(ep.public.investigation.data()).counts()[0]
    )
    assert (
        s.operator_snapshot()["performance"]["decision_diagnostics"]["final_evidence"][
            "remaining_worlds"
        ]
        == posterior.counts()[0]
    )
    act(s, FinishAction())
    repeated = s.operator_snapshot()["performance"]["decision_diagnostics"]
    assert repeated["final_evidence"]["remaining_worlds"] == posterior.counts()[0]
    assert repeated["submissions"][-1]["evidence"]["classification"] == "contradicted"
    result = public_policy(s, ep.public.evidence_files)
    assert result.victory_code and result.current_turn < 64
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"


@pytest.mark.parametrize("family", FAMILIES)
def test_stock_copy_cannot_replace_actual_mission_carrier(family):
    ep = episode(family)
    s = Session(ep)
    act(s, TakeAction(artifact="blank-stock"))
    copy = s.observe().carried_artifacts[0].id
    install(s, module(family, "laws").target(ep.investigation_truth.data()), copy)
    assert not act(s, FinishAction()).victory_code
    assert s.state.stocks["blank-stock"].remaining is None


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize(
    "machine,settings", [("reader", (9,)), ("assembler", (0,)), ("reader", (0, 1, 2, 0, 1, 2, 0))]
)
def test_invalid_configure_is_free_atomic_and_truth_independent(family, machine, settings):
    messages = set()
    for seed in (0, 767):
        s = Session(episode(family, seed))
        before = canonical_hash(s.state)
        result = s.act(0, ConfigureAction(machine=machine, settings=settings))
        assert not result.ok and before == canonical_hash(s.state)
        messages.add(result.message)
    assert len(messages) == 1


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("field", ["seed", "evidence", "state", "metadata", "disclosure"])
def test_compiled_contract_rejects_tampering(family, field):
    raw = episode(family, theory=2).model_dump(mode="json")
    if field == "seed":
        raw["construction_seed"] += 1
    elif field == "evidence":
        raw["public"]["evidence_files"]["theory.json"] = "{}"
    elif field == "state":
        raw["public"]["initial_state"]["machines"]["reader"]["settings"] = [9]
    elif field == "metadata":
        raw["generation_metadata"]["guaranteed_policy_action_count"] = 1
    else:
        raw["public"]["investigation"]["payload"]["theory"] = 3
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(raw)


@pytest.mark.parametrize("family", FAMILIES)
def test_hidden_structure_and_assignment_do_not_change_t3_evidence(family):
    assert episode(family, 0).public.evidence_files == episode(family, 123849).public.evidence_files


@pytest.mark.parametrize("family", FAMILIES)
def test_t0_discloses_a_literal_working_construction_without_inference(family):
    ep = episode(family, theory=0)
    construction = json.loads(ep.public.evidence_files["theory.json"])["resolved_construction"]
    s = Session(ep)
    act(s, TakeAction(artifact="carrier"))
    install(s, tuple(construction))
    result = act(s, FinishAction())
    assert result.victory_code and result.current_turn == 4
    assert result.performance.measurements_used == 0
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    for theory in (2, 3):
        assert (
            json.loads(episode(family, theory=theory).public.evidence_files["theory.json"])[
                "resolved_construction"
            ]
            is None
        )


def test_rejected_naive_designs_retain_their_shortcuts():
    from itertools import product
    from math import prod

    # A rotated three-bit register has eight distinguishable predictive states,
    # but a fixed three-read schedule exposes all of them.
    signatures = []
    for state in product(range(2), repeat=3):
        view = []
        for _ in range(3):
            view.append(state[0])
            state = state[1:] + state[:1]
        signatures.append(tuple(view))
    assert len(set(signatures)) == 8
    # Equal first/pairwise marginals alone do not create a hard parity problem.
    for parity in (-1, 1):
        support = [p for p in product((-1, 1), repeat=3) if prod(p) == parity]
        assert all(sum(p[j] for p in support) == 0 for j in range(3))
        assert all(sum(p[a] * p[b] for p in support) == 0 for a, b in ((0, 1), (0, 2), (1, 2)))
        assert all(prod(p) == parity for p in support)  # one joint reading solves it


@pytest.mark.slow
@pytest.mark.parametrize("family,worlds", [(FAMILIES[0], 768), (FAMILIES[1], 120), (FAMILIES[2], 384)])
def test_every_mechanism_has_supported_live_t2_and_t3_policies(family, worlds):
    for seed in range(worlds):
        for theory in (2, 3):
            ep = episode(family, seed=seed, theory=theory)
            result = public_policy(Session(ep), ep.public.evidence_files)
            assert result.victory_code
            assert result.performance.decision_diagnostics.escape_classification == "supported_win"
            assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
