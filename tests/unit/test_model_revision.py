"""Independent qualification, selective revision, equivalent builds and controls."""

import json
from dataclasses import replace

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
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.inference import Measurement
from nexus.ontology.revision.inference import Belief
from nexus.ontology.revision.laws import (
    PROGRAMS,
    QUERIES,
    QUERY_INDEX,
    accepted,
    class_id,
    compiled,
    prior_mask,
    read,
    selection,
    specification,
)
from nexus.ontology.revision.proof import prove, scalar_counterexample
from nexus.ontology.revision.qualification import QualificationLimit, audit, minimum_certificate
from nexus.ontology.revision.schema import GenerationOptions, Investigation
from nexus.protocol.session import Session
from nexus.solver.finite_machine import FiniteMachine


def episode(seed=5866, *, theory=3, guidance="provisional"):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="model-revision-v1",
        theory_level=theory,
        discovery_level=0 if theory == 0 else 5,
        planning_level=0,
        resource_pressure=1,
        ontology_options={"guidance": guidance},
        verifier_secret="revision-test-secret",
    )


def act(session, action):
    return session.act(expected_turn=session.status().turn, action=action)


def test_exhaustive_independent_conservation_behavior_and_reading_proof():
    result = prove()
    assert result["passed"] and result["behavior_classes"] == 748
    assert result["independent_transitions"] == 2_322_432
    assert result["independent_all_history_equivalence_checks"] == 20_736


@pytest.mark.parametrize("seed", [5866, 6464, 5431, 1101])
def test_selected_worlds_require_four_readings_and_mixed_mode_inference(seed):
    world = selection(seed)
    spec = specification(world, 3, 5)
    result = audit(spec, world)
    assert result["minimum_reading_only_certificate"] == 4
    assert result["minimum_supported_actions"] == 12
    assert result["combined_single_mode_all_history_closure"] > 1
    assert result["minimum_additional_reading_certificate_after_counterexample"] >= 3
    assert result["order_sensitive_witness"]
    assert result["provisional_matches_archive"] and not result["provisional_is_globally_valid"]
    # Product traversal in an independent scalar implementation agrees exactly.
    assert scalar_counterexample(world.program, spec.provisional) == tuple(
        result["provisional_counterexample"]
    )
    posterior = Belief(spec)
    for query in result["certificate_queries"]:
        posterior.observe(
            Measurement("reader", {"query": query, "values": read(world.program, query)})
        )
    assert posterior.supports(world.program)


def test_search_cap_blocks_and_shallow_negative_control_is_detected():
    world = selection(5866)
    with pytest.raises(QualificationLimit, match="no admission"):
        minimum_certificate(
            prior_mask(specification(world, 3, 5)), class_id(world.program), max_nodes=0
        )
    shallow = selection(468)
    assert audit(specification(shallow, 3, 5), shallow)["minimum_reading_only_certificate"] == 1


def test_provisional_model_never_filters_truth_or_changes_paired_world():
    left, right = episode(guidance="principles"), episode(guidance="provisional")
    assert left.investigation_truth == right.investigation_truth
    a, b = left.public.investigation.data(), right.public.investigation.data()
    assert a.archive == b.archive and prior_mask(a) == prior_mask(b)
    assert left.public.initial_state == right.public.initial_state
    assert not accepted(right.investigation_truth.data(), b.provisional)
    # Even an independently supplied alternative explanation is not evidence.
    altered = b.model_copy(update={"provisional": (0, 0, 0, 0)})
    assert prior_mask(altered) == prior_mask(b)
    # Compiled episodes still reject an altered generator disclosure.
    bad = right.model_dump(mode="json")
    bad["public"]["investigation"]["payload"]["provisional"] = [0, 0, 0, 0]
    with pytest.raises(ValueError, match="disclosure"):
        PrivateEpisode.model_validate(bad)


@pytest.mark.parametrize(
    "theory,guidance", [(0, "principles"), (3, "principles"), (3, "provisional")]
)
def test_public_policy_serialization_replay_and_qualification(theory, guidance):
    ep = PrivateEpisode.model_validate_json(
        episode(theory=theory, guidance=guidance).model_dump_json()
    )
    session = Session(ep)
    result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code and result.current_turn <= 18
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed


def test_wrong_inherited_build_is_recoverable_and_equivalent_wirings_win():
    ep = episode()
    session = Session(ep)
    spec = ep.public.investigation.data()
    for action in (
        TakeAction(artifact="carrier"),
        ConfigureAction(machine="assembler", settings=spec.provisional),
        OperateAction(machine="assembler", artifact="carrier"),
    ):
        assert act(session, action).ok
    failed = act(session, FinishAction())
    assert failed.ok and failed.victory_code is None and session.status().status.value == "active"
    result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code and result.performance.failed_finishes == 1
    world = ep.investigation_truth.data()
    alias = next(
        p for p in PROGRAMS if p != world.program and class_id(p) == class_id(world.program)
    )
    assert accepted(world, alias)


def test_probe_immutability_and_invalid_control_rollback():
    session = Session(episode())
    assert act(session, TakeAction(artifact="carrier")).ok
    before = canonical_hash(session.state)
    assert not act(session, ConfigureAction(machine="reader", settings=(2,))).ok
    assert canonical_hash(session.state) == before
    specimen = session.state.artifacts["carrier"].model_dump()
    assert act(session, ProbeAction(machine="reader", artifact="carrier")).ok
    assert session.state.artifacts["carrier"].model_dump() == specimen
    assert session.status().turn == 2


def test_finite_machine_all_history_acceptance_detects_a_late_counterexample():
    left = FiniteMachine((0,) * 11, (tuple(range(1, 11)) + (10,),))
    right = replace(left, outputs=(0,) * 10 + (1,))
    assert left.counterexample(right) == (0,) * 10
    assert left.signature() != right.signature()
    relabelled = FiniteMachine((0, 0), ((1, 1),))
    assert left.signature() == relabelled.signature()


def test_the_public_prior_has_exactly_the_archive_consistent_behaviors():
    spec = episode().public.investigation.data()
    posterior = Belief(spec)
    prior = compiled()
    assert posterior.counts()[0] == sum(tuple(row[:2]) == spec.archive for row in prior.rows)
    for query in ((0, 1, 0), (1, 1, 0, 0)):
        values = read(selection(5866).program, query)
        posterior.observe(Measurement("reader", {"query": query, "values": values}))
        q = QUERY_INDEX[query]
        assert all(
            row[q] == values[0] for i, row in enumerate(prior.rows) if posterior.mask >> i & 1
        )
    payload = json.loads(episode().public.evidence_files["theory.json"])
    assert "seed" not in payload and "certificate_queries" not in payload
    assert payload["primitive_laws"]["initial_inventory"] == [2, 1, 1, 1]


def test_options_and_disclosures_reject_unsupported_shapes():
    with pytest.raises(ValueError):
        GenerationOptions(guidance="magic")
    with pytest.raises(ValueError):
        Investigation(
            theory=3, discovery=5, archive=(0, 0), guidance="principles", resolved=(0, 0, 0, 0)
        )


def test_minimum_certificate_matches_independent_brute_force_on_small_priors():
    from itertools import combinations

    prior = compiled()
    for truth in (0, 100, 350, 600, 747):
        members = (truth, *((truth + i * 53) % len(prior.rows) for i in range(1, 9)))
        mask = sum(1 << i for i in members)
        observed = tuple(
            {
                sum(1 << i for i in members if prior.rows[i][q] == prior.rows[truth][q])
                for q in range(len(QUERIES))
            }
        )
        expected = None
        for depth in range(4):
            for panel in combinations(observed, depth):
                remaining = mask
                for matching in panel:
                    remaining &= matching
                if remaining == 1 << truth:
                    expected = depth
                    break
            if expected is not None:
                break
        assert expected is not None
        assert minimum_certificate(mask, truth).readings == expected


def test_single_mode_ambiguity_uses_independent_unbounded_product_oracle():
    prior = compiled()
    for seed in (5866, 6464, 5431, 1101):
        world = selection(seed)
        spec = specification(world, 3, 5)
        compatible = [
            p for p, row in zip(prior.representatives, prior.rows) if tuple(row[:2]) == spec.archive
        ]
        both = sum(
            all(scalar_counterexample(world.program, p, modes=(m,)) is None for m in (0, 1))
            for p in compatible
        )
        assert both == audit(spec, world)["combined_single_mode_all_history_closure"]
        assert both > 1


@pytest.mark.slow
def test_live_public_policy_wins_every_behavior_class():
    from nexus.ontology.revision.laws import PROGRAM_INDEX

    for program in compiled().representatives:
        ep = episode(PROGRAM_INDEX[program], guidance="principles")
        session = Session(ep)
        result = public_policy(session, ep.public.evidence_files)
        assert result.victory_code and result.current_turn <= 18, program
        assert result.performance.decision_diagnostics.escape_classification == "supported_win"
        assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
