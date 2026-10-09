import importlib.util
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.engine.canonical import canonical_hash
from nexus.engine.investigation import response, settings
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode, qualify_episode
from nexus.generator.investigation import base_spec, compile_problem
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.solver.finite_experiments import FiniteExperimentProblem

ROOT = Path(__file__).resolve().parents[2]
module_spec = importlib.util.spec_from_file_location(
    "scientific_poc", ROOT / "scripts/scientific_investigation_poc.py"
)
poc = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(poc)


def episode(d=5, t=3, p=0, r=0, seed=7):
    return generate_episode(
        seed,
        axis_version=2,
        discovery_level=d,
        theory_level=t,
        planning_level=p,
        resource_pressure=r,
        verifier_secret="test-science-secret",
    )


def act(session, **action):
    result = session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))
    assert result.ok, result.message
    return result


@pytest.mark.parametrize("t", [1, 2, 3])
def test_exhaustive_independent_formula_oracle_and_information_cost(t):
    e = episode(d=4, t=t)
    spec = e.public.investigation
    worlds, problem = compile_problem(base_spec(spec))
    _, oracle_rows, oracle_predictions = poc.build_problem(t, True, scale=spec.scale)
    labels = {}
    for index, world in enumerate(worlds):
        for q in range(17):
            for source in ("reference", "0", "1"):
                a = 0 if source == "reference" else world.properties[int(source)]
                exact = spec.scale * (a * q * (q - 1) + world.coefficient * q**world.exponent) % 17
                assert response(world, source, q) == exact
        actual = settings(spec, world)
        assert actual == oracle_predictions[index]
        labels.setdefault(actual, problem.predictions[index])
        assert labels[actual] == problem.predictions[index]
    assert dict(problem.experiments) == oracle_rows
    assert (
        problem.minimum_guaranteed_measurements()
        == poc.oracle(tuple(oracle_rows.values()), oracle_predictions)(tuple(range(len(worlds))))
        == t + 2
    )
    assert (
        problem.minimum_fixed_measurements()
        == poc.fixed_cost(tuple(oracle_rows.values()), oracle_predictions)
        == t + 3
    )


@pytest.mark.parametrize("seed", range(15))
def test_bitmask_solver_matches_naive_oracle_on_arbitrary_small_problems(seed):
    rng = random.Random(seed)
    size = rng.randrange(2, 13)
    rows = tuple(tuple(rng.randrange(3) for _ in range(size)) for _ in range(4))
    predictions = tuple(rng.randrange(4) for _ in range(size))
    problem = FiniteExperimentProblem(
        tuple(map(str, range(size))),
        tuple((str(i), row) for i, row in enumerate(rows)),
        predictions,
    )
    expected = poc.oracle(rows, predictions)(tuple(range(size)))
    assert problem.minimum_guaranteed_measurements() == (None if expected == 999 else expected)
    expected_fixed = poc.fixed_cost(rows, predictions)
    assert problem.minimum_fixed_measurements() == (
        None if expected_fixed == 999 else expected_fixed
    )
    for i in range(size):
        observed = (("0", rows[0][i]),)
        expected = poc.oracle(rows, predictions)(
            tuple(j for j in range(size) if rows[0][j] == rows[0][i])
        )
        assert problem.minimum_guaranteed_measurements(observed) == (
            None if expected == 999 else expected
        )


PROFILES = (
    [(0, t) for t in range(4)] + [(1, 1)] + [(d, t) for d in range(2, 6) for t in range(1, 4)]
)


@pytest.mark.parametrize("d,t", PROFILES)
def test_supported_profiles_have_exact_information_certificates_and_realizable_plans(d, t):
    e = episode(d=d, t=t, p=1, r=1)
    session = Session(e)
    for action in e.reference_plan:
        result = session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))
        assert result.ok
        if session.state.terminal_status.value == "active":
            assert result.performance is None
    assert session.state.terminal_status.value == "won"
    assert result.performance.first_submission_correct
    assert result.performance.target_classes_before_first_submission == 1
    cert = e.generation_metadata.investigation_certificate
    expected = 0 if d == 0 else 1 if d == 1 else t + 1 + (d >= 4)
    assert cert["minimum_measurements"] == expected
    assert cert["adaptive_gap"] == (1 if d >= 4 else 0)
    assert cert["construction_required"] == (d == 5)
    assert canonical_hash(replay(e, session.trace)) == canonical_hash(session.state)
    assert PrivateEpisode.model_validate_json(e.model_dump_json()) == e


@pytest.mark.parametrize("p,r", [(p, r) for p in range(4) for r in range(3)])
def test_planning_and_resources_do_not_change_scientific_truth(p, r):
    control = episode(p=0, r=0)
    e = episode(p=p, r=r)
    assert e.investigation_truth == control.investigation_truth
    assert len(e.public.rooms) == p + 1
    assert (e.public.initial_state.resources.actions_remaining is None) == (r == 0)
    state, trace = execute_with_trace(
        e, [ACTION_ADAPTER.validate_python(a) for a in e.reference_plan]
    )
    assert state.terminal_status.value == "won"
    assert trace[-1].victory_code


def test_stock_copy_preparation_and_irreversible_recovery_without_clone_exploit():
    e = episode(t=1)
    session = Session(e)
    first = act(session, type="take", artifact="S0-0").events[0]["details"]["artifact"]
    before = canonical_hash(session.state)
    preview = act(session, type="probe", machine="prepare", artifact=first)
    assert preview.events[0]["details"]["result"]["sample"]["q"] == 1
    assert session.state.artifacts[first].sample.q == 0
    act(session, type="operate", machine="prepare", artifact=first)
    act(session, type="operate", machine="prepare", artifact=first)
    act(session, type="drop", artifact=first)
    act(session, type="take", artifact=first)
    assert len(session.state.artifacts) == 1
    assert session.state.artifacts[first].sample.q == 2
    second = act(session, type="take", artifact="S0-0").events[0]["details"]["artifact"]
    assert second != first and session.state.artifacts[second].sample.q == 0
    assert session.state.stocks["S0-0"].remaining is None
    assert session.state.machines["prepare"].uses_remaining is None
    assert session.state.resources.actions_remaining is None
    assert session.state.turn == 7 and canonical_hash(session.state) != before
    for machine in ("prepare", "controller"):
        current = canonical_hash(session.state)
        result = session.act(
            session.state.turn,
            ACTION_ADAPTER.validate_python(
                {"type": "probe", "machine": machine, "artifact": first}
            ),
        )
        assert not result.ok and canonical_hash(session.state) == current


def test_goal_failure_is_recoverable_with_no_component_feedback_and_terminal_metrics():
    e = episode()
    client = TestClient(create_single_session_app(e))
    initial = client.get("/observe").json()
    assert initial["actions_remaining"] is None
    assert all(s["remaining"] is None for s in initial["visible_stocks"])
    target = settings(e.public.investigation, e.investigation_truth)
    wrong = list(target)
    wrong[-1] = (wrong[-1] + 1) % 17
    for turn, action in enumerate(
        [{"type": "configure", "machine": "controller", "settings": wrong}, {"type": "finish"}]
    ):
        result = client.post("/action", json={"expected_turn": turn, "action": action}).json()
        assert result["ok"] and "performance" not in result and "victory_code" not in result
    assert result["events"] == [{"type": "finish_rejected", "details": {}}]
    assert client.get("/status").json()["status"] == "active"
    client.post(
        "/action",
        json={
            "expected_turn": 2,
            "action": {"type": "configure", "machine": "controller", "settings": target},
        },
    )
    result = client.post("/action", json={"expected_turn": 3, "action": {"type": "finish"}}).json()
    assert result["victory_code"]
    metrics = result["performance"]
    assert metrics["first_submission_correct"] is False
    assert metrics["controller_submissions"] == 2 and metrics["failed_finishes"] == 1
    assert metrics["measurements_used"] == 0 and metrics["termination_reason"] == "victory"
    assert metrics["initial_action_budget"] is None and metrics["budget_remaining"] is None
    assert client.post("/finalize").json()["performance"] == metrics


def test_active_surfaces_and_all_truths_share_public_contract():
    e = episode()
    worlds, _problem = compile_problem(base_spec(e.public.investigation))
    client = TestClient(create_single_session_app(e))
    for path in ("/observe", "/status", "/manifest", "/events"):
        text = client.get(path).text
        for private in (
            "investigation_truth",
            "investigation_certificate",
            "reference_plan",
            "verifier_secret",
            "construction_seed",
            "target_classes",
        ):
            assert private not in text
    assert len({settings(e.public.investigation, w) for w in worlds}) == 60
    # All truth changes leave initial state and evidence byte-for-byte unchanged.
    for truth in worlds:
        candidate = e.model_copy(update={"investigation_truth": truth})
        assert candidate.public == e.public


def test_d5_no_raw_experiment_set_can_identify_field_settings():
    e = episode()
    _, problem = compile_problem(base_spec(e.public.investigation))
    raw = FiniteExperimentProblem(
        problem.hypotheses,
        tuple((n, row) for n, row in problem.experiments if not n.endswith(":2")),
        problem.predictions,
    )
    assert raw.minimum_guaranteed_measurements() is None


@pytest.mark.parametrize("d,t", [(2, 1), (3, 1), (4, 2), (5, 3)])
def test_qualification_replays_every_prior_truth(d, t):
    report = qualify_episode(episode(d=d, t=t, p=1, r=1))
    assert report.passed, report
    assert report.checks["all_truths_physically_solvable"]


def test_unsupported_cells_reject_instead_of_relabeling_difficulty():
    for d, t in ((3, 0), (1, 2), (1, 3)):
        with pytest.raises(ValueError, match="axes-v2"):
            episode(d=d, t=t)


def test_finalization_is_terminal_and_distinct_from_in_world_exhaustion():
    session = Session(episode())
    status, metrics = session.finalize_attempt()
    assert status.status.value == "failed" and metrics.termination_reason == "harness_finalization"
    result = session.act(0, ACTION_ADAPTER.validate_python({"type": "take", "artifact": "S0-0"}))
    assert not result.ok and result.performance.first_submission_correct is None


def test_scientific_terminal_schema_and_null_resource_transport(monkeypatch):
    from nexus.protocol import transport
    from nexus.protocol.investigation_metrics import SCIENCE_SCHEMA_URL

    client = TestClient(create_single_session_app(episode()))
    monkeypatch.setattr(
        transport,
        "_json_request",
        lambda base, method, path, payload=None, **kwargs: client.request(
            method, path, json=payload
        ).json(),
    )
    assert transport._status("http://test")[2] is None
    status = transport._finalize("http://test")
    assert status[1] == "failed" and status[2] is None
    payload = status[-1]
    schema = json.loads((ROOT / "schemas/performance-scientific-v1.schema.json").read_text())
    assert set(payload) == set(schema["properties"]) == set(schema["required"])
    assert schema["additionalProperties"] is False
    assert payload["$schema"] == SCIENCE_SCHEMA_URL
    assert "dd6564d848183d9f70eca474a6ef02c5ab84a58e" in SCIENCE_SCHEMA_URL


def test_fixed_seed_and_secret_reproduce_scientific_episode_and_receipt():
    left, right = episode(), episode()
    assert left == right


def test_known_rescaling_preserves_information_partitions():
    from nexus.generator.investigation import make_spec

    _, control = compile_problem(make_spec(4, 3, 1, ""))
    for scale in (2, 7, 16):
        _, candidate = compile_problem(make_spec(4, 3, scale, ""))
        assert candidate.prediction_masks == control.prediction_masks
        assert [sorted(mask for _, mask in row) for row in candidate.partitions] == [
            sorted(mask for _, mask in row) for row in control.partitions
        ]


@pytest.mark.parametrize(
    "tamper", ["goal", "stock", "uses", "fixed", "disclosure", "range", "missing_stock"]
)
def test_qualification_rejects_profile_bypasses_and_forged_certificates(tamper):
    from nexus.models.goals import GoalPredicate
    from nexus.models.investigation import SpecimenStock

    e = episode(t=1)
    if tamper == "goal":
        e.public.goal = GoalPredicate(kind="phase_equals", value=0)
    elif tamper == "stock":
        e.public.initial_state.stocks["S0-2"] = SpecimenStock(
            id="S0-2", source="0", q=2, location="R0"
        )
    elif tamper == "uses":
        e.public.initial_state.machines["meter"].uses_remaining = 1
    elif tamper == "fixed":
        e.generation_metadata.investigation_certificate["fixed_measurements"] = 999
    elif tamper == "disclosure":
        e.public.investigation = e.public.investigation.model_copy(
            update={"resolved_settings": settings(e.public.investigation, e.investigation_truth)}
        )
    elif tamper == "range":
        e.public.investigation = e.public.investigation.model_copy(
            update={"target_q": (1, 2, 4, 5)}
        )
    elif tamper == "missing_stock":
        e.public.initial_state.stocks.clear()
    assert not qualify_episode(e).passed
