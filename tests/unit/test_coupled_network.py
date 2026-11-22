from __future__ import annotations

import importlib.util
import random
from functools import cache
from itertools import combinations
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.engine.network import prepare
from nexus.engine.replay import execute_with_trace
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PrivateEpisode
from nexus.models.goals import GoalKind
from nexus.models.network import NetworkSample, NetworkStock
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session
from nexus.solver.finite_experiments import FiniteExperimentProblem

ROOT = Path(__file__).resolve().parents[2]


module_spec = importlib.util.spec_from_file_location(
    "network_poc", ROOT / "scripts/coupled_network_poc.py"
)


poc = importlib.util.module_from_spec(module_spec)


module_spec.loader.exec_module(poc)


def episode(d=5, p=0, r=0, seed=7, t=3):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="coupled-network-v1",
        discovery_level=d,
        theory_level=t,
        planning_level=p,
        resource_pressure=r,
        verifier_secret="network-test-secret",
    )


def test_independent_matrix_shortcut_interpolation_and_preparation_proof():
    result = poc.prove()
    assert result["cases"][2]["axes_and_diagonal"]["ambiguous_worlds"] == 145
    assert result["preparation"]["max_origin_to_bench_operations"] == 4


def test_exact_optimized_solvers_against_arbitrary_tuple_oracles():
    rng = random.Random(49011)
    for _ in range(200):
        n, m = rng.randrange(1, 9), rng.randrange(6)
        rows = tuple((str(i), tuple(rng.randrange(4) for _ in range(n))) for i in range(m))
        targets = tuple(rng.randrange(4) for _ in range(n))
        problem = FiniteExperimentProblem(tuple(map(str, range(n))), rows, targets)

        @cache
        def oracle(belief, targets=targets, rows=rows):
            if len({targets[i] for i in belief}) == 1:
                return 0
            best = None
            for _, row in rows:
                groups = {}
                for i in belief:
                    groups.setdefault(row[i], set()).add(i)
                if len(groups) == 1:
                    continue
                costs = [oracle(frozenset(g)) for g in groups.values()]
                if any(v is None for v in costs):
                    continue
                value = 1 + max(costs)
                best = value if best is None else min(best, value)
            return best

        for mask in range(1, 1 << n):
            assert problem._cost(mask) == oracle(frozenset(i for i in range(n) if mask & (1 << i)))
        expected = None
        for size in range(m + 1):
            for chosen in combinations(range(m), size):
                groups = {}
                for i in range(n):
                    groups.setdefault(tuple(rows[j][1][i] for j in chosen), set()).add(targets[i])
                if all(len(g) == 1 for g in groups.values()):
                    expected = size
                    break
            if expected is not None:
                break
        assert problem.minimum_fixed_measurements() == expected


@pytest.mark.parametrize("d", [4, 5])
@pytest.mark.parametrize("p,r", [(p, r) for p in range(4) for r in range(3)])
def test_all_supported_physical_profiles_reference_win(d, p, r):
    e = episode(d, p, r)
    state, trace = execute_with_trace(
        e, [ACTION_ADAPTER.validate_python(a) for a in e.reference_plan]
    )
    assert state.terminal_status == "won" and trace[-1].victory_code
    assert PrivateEpisode.model_validate_json(e.model_dump_json()) == e
    assert (e.public.initial_state.resources.actions_remaining is None) == (r == 0)
    assert state.turn <= e.generation_metadata.guaranteed_policy_action_count


@pytest.mark.slow
@pytest.mark.parametrize("d,p,r", [(4, 1, 1), (5, 2, 2)])
def test_every_complete_prior_world_physically_wins(d, p, r):
    report = qualify_episode(episode(d, p, r))
    assert report.passed, report.errors
    assert report.metrics["worlds_replayed"] == 2187


@pytest.mark.parametrize("d,t", [(3, 3), (4, 2), (5, 1), (1, 0)])
def test_unqualified_axis_cells_reject(d, t):
    with pytest.raises(ValueError, match="supports"):
        episode(d=d, t=t)


def test_no_field_preview_or_active_telemetry_and_terminal_consistency():
    e = episode()
    client = TestClient(create_single_session_app(e))
    for route in ("/manifest", "/observe", "/status"):
        assert "performance" not in client.get(route).json()
    theory = client.get("/evidence/theory.json")
    assert theory.status_code == 200
    for a in e.reference_plan:
        o = client.post(
            "/action", json={"expected_turn": client.get("/status").json()["turn"], "action": a}
        ).json()
        assert o["ok"]
        if o["observation"]["terminal_status"] == "active":
            assert "performance" not in o
    assert "performance" not in o
    metrics = client.post("/finalize").json()["performance"]
    assert metrics["first_submission_correct"]
    assert metrics["target_classes_before_first_submission"] == 1
    assert metrics["certificate"]["structural_programs"] == 27
    s = Session(episode())

    def act(**a):
        return s.act(s.state.turn, ACTION_ADAPTER.validate_python(a))

    result = act(type="take", artifact="S0-0")
    artifact = result.events[0]["details"]["artifact"]
    before = canonical_hash(s.state)
    assert not act(type="probe", machine="controller", artifact=artifact).ok
    assert canonical_hash(s.state) == before
    s.state.artifacts[artifact].sample = NetworkSample(x=4, y=1)
    before = canonical_hash(s.state)
    assert not act(type="probe", machine="meter", artifact=artifact).ok
    assert canonical_hash(s.state) == before


@pytest.mark.parametrize(
    "mutation",
    [
        "stock",
        "goal",
        "certificate",
        "program",
        "empty_program",
        "sample",
        "budget",
        "evidence",
        "reference",
    ],
)
def test_qualifier_rejects_compiled_contract_tampering(mutation):
    e = episode()
    if mutation == "stock":
        e.public.initial_state.stocks["S1-1"] = NetworkStock(id="S1-1", location="R0", x=1, y=1)
    elif mutation == "goal":
        e.public.goal = e.public.goal.model_copy(update={"kind": GoalKind.AND, "children": ()})
    elif mutation == "certificate":
        e.generation_metadata.investigation_certificate["fixed_measurements"] = 5
    elif mutation == "program":
        e.investigation_truth = e.investigation_truth.model_copy(
            update={"program": tuple(reversed(e.investigation_truth.program))}
        )
    elif mutation == "sample":
        e.public.initial_state.stocks["S0-0"].x = 1
    elif mutation == "empty_program":
        e.investigation_truth = e.investigation_truth.model_copy(update={"program": ()})
    elif mutation == "budget":
        e.public.initial_state.resources.actions_remaining = 10
    elif mutation == "evidence":
        e.public.evidence_files["theory.json"] += " altered"
    else:
        e.reference_plan = ({"type": "finish"},)
    assert not qualify_episode(e).passed


def test_cross_family_stock_and_sample_validation():
    from nexus.models.investigation import SampleState, SpecimenStock

    e = episode()
    e.public.investigation = None
    e.investigation_truth = None
    with pytest.raises(ValueError, match="require an investigation"):
        PrivateEpisode.model_validate_json(e.model_dump_json())
    e = episode()
    e.public.initial_state.stocks = {"bad": SpecimenStock(id="bad", location="R0", source="0", q=0)}
    with pytest.raises(ValueError, match="families"):
        PrivateEpisode.model_validate_json(e.model_dump_json())

    for network in (True, False):
        e = (
            episode()
            if network
            else generate_episode(7, axis_version=2, theory_level=3, discovery_level=5)
        )
        session = Session(e)
        stock = next(iter(session.state.stocks))
        result = session.act(0, ACTION_ADAPTER.validate_python({"type": "take", "artifact": stock}))
        assert result.ok
        artifact = session.state.artifacts[result.events[0]["details"]["artifact"]]
        artifact.sample = SampleState(source="0", q=0) if network else NetworkSample(x=0, y=0)
        e.public.initial_state = session.state
        with pytest.raises(ValueError, match="families"):
            PrivateEpisode.model_validate_json(e.model_dump_json())
    e = generate_episode(7, axis_version=2, theory_level=3, discovery_level=5)
    e.public.initial_state.stocks = {"bad": NetworkStock(id="bad", location="R0", x=0, y=0)}
    with pytest.raises(ValueError, match="families"):
        PrivateEpisode.model_validate_json(e.model_dump_json())


def test_seed_pairing_program_diversity_and_baseline_preservation():
    gates = set()
    for seed in (7, 17, 23, 41, 73):
        left = episode(d=4, p=1, r=1, seed=seed)
        right = episode(d=5, p=2, r=0, seed=seed)
        assert left.investigation_truth == right.investigation_truth
        gates.add(left.investigation_truth.gates)
    assert len(gates) >= 4
    left = generate_episode(
        7, axis_version=2, discovery_level=5, theory_level=3, verifier_secret="fixed"
    )
    right = generate_episode(
        7,
        axis_version=2,
        discovery_level=5,
        theory_level=3,
        verifier_secret="fixed",
        science_family="shared-response-v1",
    )
    assert left == right
    assert prepare(prepare((0, 0), "shift"), "shear") == (1, 2)
    assert prepare(prepare((0, 0), "shear"), "shift") == (1, 1)


def test_cli_family_environment_and_human_rendering(monkeypatch):
    from io import StringIO

    import uvicorn
    from rich.console import Console

    from nexus.render.observer import render_observer

    captured = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: captured.update(app=app))
    result = CliRunner().invoke(
        app,
        ["serve-session", "--seed", "7"],
        env={
            "NEXUS_AXIS_VERSION": "2",
            "NEXUS_SCIENCE_FAMILY": "coupled-network-v1",
            "NEXUS_THEORY_LEVEL": "3",
            "NEXUS_DISCOVERY_LEVEL": "5",
        },
    )
    assert result.exit_code == 0, result.output
    client = TestClient(captured["app"])
    assert "coupled" in client.get("/manifest").json()["description"]
    e = episode()
    s = Session(e)
    s.act(0, ACTION_ADAPTER.validate_python({"type": "take", "artifact": "S0-0"}))
    stream = StringIO()
    render_observer(e, s.state, console=Console(file=stream))
    assert "(0, 0)" in stream.getvalue()
