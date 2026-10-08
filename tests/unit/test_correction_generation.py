import json
import logging
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.generator.correction import read_correction_prior
from nexus.generator.generator import _candidate_rules_for_episode
from nexus.generator.qualify import qualify_episode
from nexus.models.episode import PrivateEpisode
from nexus.protocol.session import Session


@pytest.mark.parametrize("planning,resource", [(p, r) for p in range(4) for r in range(3)])
def test_t2_profiles_are_qualified_and_replay_every_viable_law(planning, resource, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from profile_theory import replay_policy
    world = generate_episode(17, theory_level=2, discovery_level=2,
                             planning_level=planning, resource_pressure=resource)
    assert qualify_episode(world).passed
    assert len(_candidate_rules_for_episode(world)["M1"]) == 9
    assert replay_policy(world, _candidate_rules_for_episode(world)) == 5
    assert world.generation_metadata.theory_level == 2
    if resource == 2:
        assert world.generation_metadata.action_budget == world.generation_metadata.guaranteed_policy_action_count


@pytest.mark.parametrize("discovery", [0, 1, 3, 4, 5])
def test_t2_rejects_unproved_discovery_profiles(discovery):
    with pytest.raises(ValueError, match="T2 currently supports D2"):
        generate_episode(17, discovery_level=discovery, theory_level=2)


@pytest.mark.parametrize("mutation", ["theory", "manual", "calibration", "effective", "uses", "budget"])
def test_t2_qualification_rejects_broken_contracts(mutation):
    world = generate_episode(17, discovery_level=2, theory_level=2)
    if mutation == "theory":
        payload = json.loads(world.public.evidence_files["theory.json"])
        payload["correction_add_choices"] = [1]
        world.public.evidence_files["theory.json"] = json.dumps(payload)
    elif mutation == "manual":
        world.public.evidence_files["facility_manual.txt"] += " Model is exact everywhere."
    elif mutation == "calibration":
        world.public.evidence_files["measurements.csv"] = world.public.evidence_files["measurements.csv"].replace("\n0,", "\n1,")
    elif mutation == "effective":
        world.rules["law"] = read_correction_prior(world.public.evidence_files).effective()
    elif mutation == "uses":
        world.public.initial_state.machines["M1"].uses_remaining = 2
    else:
        world.public.initial_state.resources.actions_remaining -= 1
    assert not qualify_episode(world).passed


def test_t2_determinism_and_opt_in_diagnostics_do_not_change_episode(caplog):
    options = dict(seed=2525, discovery_level=2, theory_level=2, verifier_secret="private-correction-secret")
    quiet = generate_episode(**options)
    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        logged = generate_episode(**options)
    assert quiet == logged
    assert "private-correction-secret" not in caplog.text
    assert "construction_seed" not in caplog.text
    summary = caplog.records[-1].generation_summary
    assert summary["event"] == "complete"
    assert "generation.core/correction.family" in summary["stages"]
    session = Session(logged)
    assert "performance" not in session.observe().model_dump(exclude_none=True)
    assert "generation_summary" not in session.observe().model_dump_json()


def test_cli_environment_enables_t2_and_exported_episode_qualifies(tmp_path):
    out = tmp_path / "episode"
    result = CliRunner().invoke(app, ["generate", str(out), "--seed", "17", "--discovery-level", "2"],
                                env={"NEXUS_THEORY_LEVEL": "2"})
    assert result.exit_code == 0, result.output
    world = PrivateEpisode.model_validate_json((out / "private.json").read_text())
    assert world.generation_metadata.theory_level == 2
    assert qualify_episode(world).passed
