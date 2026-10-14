"""Live action coverage, exact resources, public inference and real finish/receipt."""

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.domain import DomainTruth
from nexus.ontology.repair.generation import generate_repair
from nexus.ontology.repair.laws import worlds
from nexus.ontology.repair.policy import public_policy
from nexus.ontology.repair.qualification import qualify_repair
from nexus.ontology.repair.schema import FAMILY
from nexus.presentation import attach
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session


class Player:
    """No private episode/state/ref-plan attribute available to the reference agent."""

    def __init__(self, session):
        self.manifest = session.manifest
        self.evidence = session.evidence
        self.observe = session.observe
        self.status = session.status
        self.act = session.act


@pytest.mark.slow
def test_every_truth_reaches_actual_victory_through_three_public_rounds():
    base = attach(generate_repair(0, verifier_secret="all-worlds"))
    for index, world in enumerate(worlds()):
        episode = base.model_copy(
            update={
                "construction_seed": index,
                "investigation_truth": DomainTruth(
                    ontology=FAMILY, payload=world.model_dump(mode="json")
                ),
            }
        )
        session = Session(episode)
        result = public_policy(Player(session))
        assert result.victory_code and result.current_turn == 15
        assert result.performance.target_classes_before_first_submission == 1
        assert result.performance.first_submission_correct
        assert session.public_transcript.snapshot()["complete"]
        # Replay covers the exact state transitions and receipt, not only arithmetic.
        assert canonical_hash(replay(episode, session.trace)) == canonical_hash(session.state)


@pytest.mark.parametrize("p", (0, 1))
@pytest.mark.parametrize("seed", (0, 38, 42, 3217, 7202))
def test_public_recovery_uses_one_policy_for_any_rejected_dose(p, seed):
    session = Session(attach(generate_repair(seed, planning_level=p, verifier_secret="recovery")))
    result = public_policy(Player(session), failed_attempt=(6, 0, 5, 2))
    assert result.victory_code
    assert result.current_turn in (5 + p, 17 + p)
    if result.current_turn == 17 + p:
        assert result.observation.actions_remaining == 0
        assert result.performance.failed_finishes == 1
        assert result.performance.first_submission_correct is False
        assert result.performance.final_submission_correct is True


def test_configure_and_probe_do_not_apply_a_key_treatment():
    session = Session(generate_repair(42, planning_level=0))
    take = lambda a: session.act(session.status().turn, a)
    take(TakeAction(artifact="seal"))
    from nexus.ontology.repair.runtime import expected

    dose = expected(session.episode)
    take(ConfigureAction(machine="doser", settings=dose))
    before = canonical_hash(session.state)
    preview = take(ProbeAction(machine="doser", artifact="seal"))
    assert preview.events[0]["details"]["result"]["payload"]["doses"] == list(dose)
    assert session.state.artifacts["seal"].data().doses is None
    rejected = take(FinishAction())
    assert not rejected.victory_code and rejected.performance is None
    take(OperateAction(machine="doser", artifact="seal"))
    win = take(FinishAction())
    assert win.victory_code and win.performance.failed_finishes == 1
    assert win.performance.final_submission_correct
    assert before != canonical_hash(session.state)


def test_free_errors_and_null_material_responses_do_not_reveal_truth():
    responses = []
    # Same public identity and initial contract in all worlds; arbitrary other IDs
    # and malformed requests are public-data-only classes at the protocol boundary.
    base = generate_repair(0, planning_level=0, verifier_secret="scope")
    for i in (0, 41, 2231, 7202):
        episode = base.model_copy(
            update={
                "construction_seed": i,
                "investigation_truth": DomainTruth(
                    ontology=FAMILY, payload=worlds()[i].model_dump(mode="json")
                ),
            }
        )
        session = Session(episode)
        session.act(0, TakeAction(artifact="seal"))
        results = []
        for action in (
            ProbeAction(machine="stage", artifact="seal"),
            ConfigureAction(machine="stage", settings=(2, 1)),
            ConfigureAction(machine="reader", settings=(1,)),
            ProbeAction(machine="missing", artifact="seal"),
            ProbeAction(machine="reference", artifact="seal"),
            ProbeAction(machine="reader", artifact="seal"),
            FinishAction(),
        ):
            r = session.act(session.status().turn, action)
            results.append(r.model_dump(mode="json", exclude_none=True))
        responses.append(results)
    assert all(r == responses[0] for r in responses)


def test_invalid_initial_budget_defaults_and_extra_disclosure_fail_qualification():
    base = generate_repair(42, planning_level=0)
    for mutate in (
        lambda e: setattr(e.public.initial_state.resources, "actions_remaining", 18),
        lambda e: setattr(e.public.initial_state.machines["stage"], "settings", (0, 0)),
        lambda e: setattr(e.public, "description", "A hidden-law hint"),
        lambda e: setattr(e, "construction_seed", 0),
        lambda e: setattr(
            e.public,
            "goal",
            e.public.goal.model_copy(update={"value": {"winning_dose": [0, 1, 2, 3]}}),
        ),
        lambda e: setattr(e.generation_metadata, "action_budget", 99),
        lambda e: e.generation_metadata.investigation_certificate.update(
            {"semantic_release_sha256": "old-release"}
        ),
        lambda e: e.public.evidence_files.update({"preview.json": "answer"}),
        lambda e: e.public.initial_state.artifacts["seal"].payload.update({"doses": [0, 0, 0, 0]}),
    ):
        changed = base.model_copy(deep=True)
        mutate(changed)
        assert not qualify_repair(changed).passed


def test_http_complete_artifact_projection_and_active_privacy():
    app = create_single_session_app(attach(generate_repair(42, planning_level=0)))
    client = TestClient(app)

    def act(turn, body):
        return client.post("/action", json={"expected_turn": turn, "action": body}).json()

    first = act(0, {"type": "take", "artifact": "stock"})
    specimen = first["events"][0]["details"]["artifact"]
    result = act(1, {"type": "probe", "machine": "reference", "artifact": specimen})
    payload = result["events"][0]["details"]["result"]["payload"]
    assert payload["reading"] is not None and payload["context"] is None
    assert "performance" not in result and "victory_code" not in result
    assert app.state.public_transcript.snapshot()["records"][-1]["response"]["body"] == result
