import importlib.util
from pathlib import Path
import sys

import pytest

from nexus.engine.rules import apply_effect
from nexus.models.world import Shape

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/theory_structure_poc.py"
spec = importlib.util.spec_from_file_location("theory_structure_poc", SCRIPT)
poc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = poc
spec.loader.exec_module(poc)


def test_factored_prior_keeps_cross_context_uncertainty_and_updates_only_observed_cell():
    prior, belief, world = poc.build_case(17)
    assert prior.cardinality == 729 and belief.cardinality == 243
    reduced, multiplicity = belief.project(world)
    assert len(reduced) == 9 and multiplicity == 27
    item = world.public.initial_state.artifacts["A1"]
    observed = apply_effect(world.rules["law"], item, 0)
    updated = belief.observe(item, 0, observed)
    assert updated.cardinality == 81
    assert len(updated.project(world)[0]) == 3
    assert updated.domains[updated.cells.index((item.shape, 1))] == (1, 2, 3)
    assert all(updated.domains[i] == belief.domains[i] for i, (shape, _) in enumerate(belief.cells)
               if shape != item.shape)
    # Repeating a measurement adds no information; its input value does not define a new cell.
    assert updated.observe(item, 0, observed) == updated


def test_projection_rejects_world_with_another_reachable_shape():
    _, belief, world = poc.build_case(17)
    item = world.public.initial_state.artifacts["A1"]
    shape = next(s for s in Shape if s != item.shape)
    world.public.initial_state.artifacts["A2"] = item.model_copy(update={"id": "A2", "shape": shape})
    with pytest.raises(ValueError, match="one artifact"):
        belief.project(world)


def test_prior_rejects_contradictory_observations_and_unsupported_domains():
    prior, _, world = poc.build_case(17)
    item = world.public.initial_state.artifacts["A1"]
    with pytest.raises(ValueError, match="contradicts"):
        prior.observe(item, 0, item)
    with pytest.raises(ValueError, match="invalid bounded"):
        poc.CellPrior(domains=((0,),) * 6)


def test_reduced_policy_matches_full_prior_oracle_and_replays_every_full_law(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    result = poc.run_case(17)
    assert result["after_evidence"] == 243
    assert result["viable_full"] == result["full_replays"] == 135
    assert result["reduced_replays"] == 5
    assert result["reachable_domain_comparisons"] == 10692
    assert result["minimum_guaranteed_probes"] == 1
