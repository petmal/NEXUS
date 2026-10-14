import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.generator.generator import _candidate_rules_for_episode
from nexus.generator.qualify import qualify_episode
from nexus.generator.theory import SPEC, theory_universe
from nexus.models.episode import PrivateEpisode
from nexus.protocol.http import create_single_session_app


@pytest.mark.parametrize("d", range(6))
def test_t0_retains_pre_theory_compiled_episode(d):
    fixture = json.loads((Path(__file__).parents[1] / "fixtures/theory-t0-baseline.json").read_text())
    # This fixture predates versioned presentation. Preserve its exact bytes;
    # current/legacy presentation execution parity is covered separately.
    episode = generate_episode(fixture["seed"], discovery_level=d, planning_level=2,
                               verifier_secret=fixture["secret"], presentation_version=None)
    explicit = generate_episode(fixture["seed"], discovery_level=d, planning_level=2,
                                theory_level=0, verifier_secret=fixture["secret"],
                                presentation_version=None)
    assert episode == explicit
    payload = episode.model_dump(mode="json")
    assert payload["generation_metadata"].pop("theory_level") == 0
    assert canonical_hash(payload) == fixture["hashes"][str(d)]
    assert PrivateEpisode.model_validate(payload) == episode


@pytest.mark.parametrize("d", range(5))
def test_t1_pairing_discovery_and_exact_budget(d):
    t0 = generate_episode(17, discovery_level=d, planning_level=2, resource_pressure=2)
    t1 = generate_episode(17, discovery_level=d, planning_level=2, resource_pressure=2, theory_level=1)
    a, b = t0.generation_metadata, t1.generation_metadata
    assert t0.rules == t1.rules
    assert t0.public.rooms == t1.public.rooms
    assert t0.public.edges == t1.public.edges
    assert t0.public.goal == t1.public.goal
    assert a.scenario_family_id == b.scenario_family_id
    assert t0.public.initial_state.artifacts == t1.public.initial_state.artifacts
    assert t0.public.episode_id != t1.public.episode_id
    assert b.theory_level == 1
    assert b.candidate_rules_before_evidence == 27120
    assert b.required_probe_count == (0, 0, 1, 2, 1)[d]
    assert b.action_budget == b.guaranteed_policy_action_count
    assert b.resource_allowance == 0
    assert qualify_episode(t1).passed
    assert t1.public.evidence_files["theory.json"] == SPEC.public_json()
    assert "add2_toggle_rotate1" not in t1.public.model_dump_json()
    assert len(_candidate_rules_for_episode(t1)) == (2 if d == 3 else 1)


@pytest.mark.parametrize("p,r", [(0, 0), (1, 1), (2, 2), (3, 2)])
def test_t1_planning_resource_profiles(p, r):
    episode = generate_episode(17, discovery_level=2, planning_level=p,
                               resource_pressure=r, theory_level=1)
    assert qualify_episode(episode).passed
    assert episode.generation_metadata.planning_level == p
    assert episode.generation_metadata.resource_pressure == r


@pytest.mark.parametrize("d,t", [(5, 1), (0, 2), (0, -1), (1, 3), (2, 4)])
def test_unsupported_theory_profiles_rejected(d, t):
    with pytest.raises(ValueError, match="T[123] currently supports|theory_level must"):
        generate_episode(17, discovery_level=d, theory_level=t)


@pytest.mark.parametrize("filename", ["theory.json", "facility_manual.txt"])
def test_tampered_public_theory_fails_qualification(filename):
    episode = generate_episode(17, discovery_level=1, theory_level=1)
    episode.public.evidence_files[filename] += " altered"
    report = qualify_episode(episode)
    assert not report.passed
    assert not report.checks["theory_prior"]


def test_t1_empty_evidence_never_truncates_public_belief():
    episode = generate_episode(17, theory_level=1)
    episode.public.evidence_files["measurements.csv"] = ""
    report = qualify_episode(episode)
    assert not report.passed
    assert "27120" in report.errors[0]


def test_t1_private_rule_cannot_depend_on_an_undisclosed_variable():
    from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
    universe = theory_universe()
    rule = Effect(kind=EffectKind.CONDITIONAL,
                  condition=Condition(kind=ConditionKind.EQUALS, field="pattern", value="plain"),
                  effects=universe.branch_ast(1), else_effects=universe.branch_ast(2))
    assert not universe.contains(rule, tuple(range(len(universe.behaviors))))


def test_t1_cli_and_service_keep_diagnostics_terminal_only(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["generate", str(tmp_path / "episode"), "--seed", "17",
                                 "--discovery-level", "2", "--theory-level", "1"])
    assert result.exit_code == 0, result.output
    episode = PrivateEpisode.model_validate_json((tmp_path / "episode/private.json").read_text())
    assert episode.generation_metadata.theory_level == 1
    client = TestClient(create_single_session_app(episode))
    for route in ("/manifest", "/observe", "/status"):
        response = client.get(route)
        assert response.status_code == 200
        assert "performance" not in response.json()
    for action in episode.reference_plan:
        response = client.post("/action", json={"expected_turn": client.get("/status").json()["turn"],
                                               "action": action})
        assert response.json()["ok"]
        if response.json()["observation"]["terminal_status"] == "active":
            assert "performance" not in response.json()
    assert response.json()["performance"]["theory_level"] == 1
    assert response.json()["performance"]["$schema"].endswith("performance-v6.schema.json")


def test_service_reads_theory_env(monkeypatch):
    import uvicorn
    captured = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: captured.update(app=app))
    result = CliRunner().invoke(app, ["serve-session", "--seed", "17"],
                                env={"NEXUS_THEORY_LEVEL": "1"})
    assert result.exit_code == 0, result.output
    client = TestClient(captured["app"])
    assert "theory.json" in client.get("/manifest").json()["evidence_files"]


@pytest.mark.parametrize("d", range(5))
def test_t1_p3_pairing_uses_the_same_t0_delivery_dependency(d):
    t0 = generate_episode(17, discovery_level=d, planning_level=3, resource_pressure=2)
    t1 = generate_episode(17, discovery_level=d, planning_level=3, resource_pressure=2, theory_level=1)
    assert t0.public.goal == t1.public.goal
    assert t0.public.initial_state.artifacts == t1.public.initial_state.artifacts
    assert t0.public.rooms == t1.public.rooms
    assert t0.public.edges == t1.public.edges
    assert t0.reference_plan == t1.reference_plan
    assert t0.generation_metadata.planning_dependency_action_cost == t1.generation_metadata.planning_dependency_action_cost
    assert qualify_episode(t1).passed


def test_broader_t1_prior_cannot_make_identical_evidence_cheaper():
    from nexus.generator.evidence import candidates_matching_csv
    from nexus.generator.rules import enumerate_transformation_rules
    from nexus.solver.belief import solve_guaranteed_policy
    episode = generate_episode(17, discovery_level=2, planning_level=0, theory_level=1)
    text = episode.public.evidence_files["measurements.csv"]
    t0 = candidates_matching_csv(text, enumerate_transformation_rules())
    t1 = theory_universe().candidates(text)
    narrow = solve_guaranteed_policy(episode, candidate_rules_by_machine={"M1": t0}, max_actions=96, include_action_values=False)
    broad = solve_guaranteed_policy(episode, candidate_rules_by_machine={"M1": t1}, max_actions=96, include_action_values=False)
    assert narrow.solvable and broad.solvable
    assert narrow.optimal_worst_case_actions <= broad.optimal_worst_case_actions


@pytest.mark.parametrize("seed,d", [(8, 1), (19, 1), (73, 3)])
def test_uncertified_paired_seed_fails_explicitly(seed, d):
    from nexus.generator.generator import GenerationError
    with pytest.raises(GenerationError, match="no hidden-law reroll or weaker D guarantee"):
        generate_episode(seed, discovery_level=d, planning_level=2, theory_level=1)
