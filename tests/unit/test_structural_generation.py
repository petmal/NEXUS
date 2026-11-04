import logging
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexus.cli import app
from nexus.engine.rules import apply_effect
from nexus.generator import generate_episode
from nexus.generator.evidence import candidates_matching_csv
from nexus.generator.generator import _candidate_rules_for_episode
from nexus.generator.qualify import qualify_episode
from nexus.generator.structural import StructuralPrior, structural_belief
from nexus.models.episode import PrivateEpisode
from nexus.models.world import Shape
from nexus.protocol.session import Session
from nexus.solver.belief import solve_guaranteed_policy


@pytest.mark.parametrize("planning,resource", [(p, r) for p in range(4) for r in range(3)])
def test_t3_profiles_qualify_and_replay_all_reachable_classes(planning, resource, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from profile_theory import replay_policy
    world = generate_episode(17, theory_level=3, discovery_level=2,
                             planning_level=planning, resource_pressure=resource)
    report = qualify_episode(world)
    assert report.passed, report
    assert report.metrics["structural_after_evidence"] == 243
    assert report.metrics["structural_class_multiplicity"] == 27
    assert replay_policy(world, _candidate_rules_for_episode(world)) == 5
    if resource == 2:
        assert world.generation_metadata.action_budget == world.generation_metadata.guaranteed_policy_action_count


@pytest.mark.parametrize("seed", [1, 17])
def test_t3_projection_matches_exhaustive_prior_and_full_law_policy(seed, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from profile_theory import replay_policy
    world = generate_episode(seed, theory_level=3, discovery_level=2, planning_level=0)
    belief = structural_belief(world)
    full = candidates_matching_csv(world.public.evidence_files["measurements.csv"], StructuralPrior().full_laws())
    assert full == belief.full_laws()
    assert world.rules["law"] in full
    reduced, multiplicity = belief.project(world)
    item = world.public.initial_state.artifacts["A1"]
    def signature(law):
        return tuple(apply_effect(law, item.model_copy(update={"value": value}), phase).model_dump_json()
                     for value in range(11) for phase in range(4))
    signatures = {signature(law): 0 for law in reduced}
    for law in full:
        signatures[signature(law)] += 1
    assert set(signatures.values()) == {multiplicity}
    exact = solve_guaranteed_policy(world, candidate_rules_by_machine={"M1": full},
                                   max_actions=96, include_action_values=False)
    assert exact.optimal_worst_case_actions == world.generation_metadata.guaranteed_policy_action_count
    assert exact.viable_hypothesis_count == 135
    world.generation_metadata.viable_causal_hypotheses = 135
    assert replay_policy(world, {"M1": full}) == 135


@pytest.mark.parametrize("mutation", ["theory", "manual", "calibration", "rule", "shape", "uses", "budget", "counts"])
def test_t3_rejects_broken_prior_projection_and_metadata(mutation):
    world = generate_episode(17, discovery_level=2, theory_level=3, planning_level=0)
    if mutation == "theory":
        world.public.evidence_files["theory.json"] = "{}"
    elif mutation == "manual":
        world.public.evidence_files["facility_manual.txt"] += " Assume additive corrections."
    elif mutation == "calibration":
        world.public.evidence_files["measurements.csv"] = world.public.evidence_files["measurements.csv"].replace("\n0,", "\n1,")
    elif mutation == "rule":
        world.rules["law"] = world.rules["law"].effects[0]
    elif mutation == "shape":
        item = world.public.initial_state.artifacts["A1"]
        world.public.initial_state.artifacts["A2"] = item.model_copy(update={
            "id": "A2", "shape": next(s for s in Shape if s != item.shape)})
    elif mutation == "uses":
        world.public.initial_state.machines["M1"].uses_remaining = 2
    elif mutation == "budget":
        world.public.initial_state.resources.actions_remaining -= 1
    else:
        world.generation_metadata.candidate_rules_before_evidence = 9
    assert not qualify_episode(world).passed


def test_t3_determinism_diagnostics_and_cli(tmp_path, caplog):
    options = dict(seed=17, theory_level=3, discovery_level=2, planning_level=0,
                   verifier_secret="private-structural-secret")
    quiet = generate_episode(**options)
    with caplog.at_level(logging.INFO, logger="nexus.generation"):
        logged = generate_episode(**options)
    assert quiet == logged
    assert "private-structural-secret" not in caplog.text
    assert "construction_seed" not in caplog.text
    assert "generation.core/structural.projection" in caplog.records[-1].generation_summary["stages"]
    assert "performance" not in Session(logged).observe().model_dump(exclude_none=True)
    out = tmp_path / "episode"
    result = CliRunner().invoke(app, ["generate", str(out), "--seed", "17", "--discovery-level", "2"],
                                env={"NEXUS_THEORY_LEVEL": "3"})
    assert result.exit_code == 0, result.output
    assert PrivateEpisode.model_validate_json((out / "private.json").read_text()).generation_metadata.theory_level == 3


@pytest.mark.parametrize("discovery", [0, 1, 3, 4, 5])
def test_t3_unsupported_discovery_profiles_fail_explicitly(discovery):
    with pytest.raises(ValueError, match="T3 currently supports D2"):
        generate_episode(17, theory_level=3, discovery_level=discovery)
