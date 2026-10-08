"""Selection must stay identical to canonical AST evaluation, including ties."""
import pytest

from nexus.engine.rules import apply_effect
from nexus.generator import evidence
from nexus.generator.rules import transformation_rule_catalog
from nexus.models.world import Artifact, Shape


@pytest.mark.parametrize("discovery", [0, 1, 2])
@pytest.mark.parametrize("shape", tuple(Shape))
def test_evidence_selection_matches_uncached_interpreter(discovery, shape, monkeypatch):
    catalog = transformation_rule_catalog()
    item = Artifact(id="A1", location="lab", shape=shape, pattern="plain", value=7,
                    orientation="east", polarity="negative")
    def outcome():
        try:
            return evidence.choose_mission_evidence(catalog[17], list(catalog), item, 1,
                                                    discovery_level=discovery)
        except evidence.EvidencePlanningError as exc:
            return str(exc)
    cached = outcome()
    class Interpreted:
        def __getitem__(self, index):
            after = apply_effect(catalog[index], item, 1)
            return after.value, after.polarity.value, after.orientation.value
    monkeypatch.setattr(evidence, "_catalog_predictions", lambda artifact, phase: Interpreted())
    assert outcome() == cached
