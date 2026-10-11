"""Cross-ontology conformance, independent inference oracle and privacy boundaries."""

import json
import subprocess
import sys
from itertools import permutations, product

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.models.actions import ConfigureAction, FinishAction, ProbeAction, TakeAction
from nexus.models.domain import DomainArtifact, DomainTruth
from nexus.models.episode import PrivateEpisode
from nexus.models.events import TraceRecord
from nexus.ontology.categorical.generation import generate_categorical, public_policy
from nexus.ontology.categorical.inference import CategoricalBelief
from nexus.ontology.categorical.runtime import FAMILY
from nexus.ontology.categorical.schema import SYMBOLS
from nexus.ontology.graph import InvestigationGraph, Node
from nexus.ontology.inference import Measurement
from nexus.protocol.http import create_single_session_app
from nexus.protocol.session import Session


@pytest.mark.parametrize("depth", [2, 3])
def test_every_admitted_world_wins_via_public_policy_and_replays(depth):
    base = generate_categorical(7, depth=depth, verifier_secret="test")
    for laws in product(tuple(permutations(range(3))), repeat=depth):
        episode = base.model_copy(deep=True)
        episode.investigation_truth = DomainTruth(
            ontology=FAMILY, payload={"laws": [list(law) for law in laws]}
        )
        episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
        session = Session(episode)
        result = public_policy(session)
        assert result.victory_code
        assert result.performance.measurements_used == 2 * depth
        assert result.performance.target_classes_before_first_submission == 1
        assert result.performance.first_submission_correct
        assert result.performance.actions_used == 4 * depth + 2
        records = [TraceRecord.model_validate_json(r.model_dump_json()) for r in session.trace]
        assert canonical_hash(replay(episode, records)) == canonical_hash(session.state)


def oracle(world, stage, value, tuning):
    upstream = value
    for law in world[:stage]:
        upstream = law[upstream]
    return None if stage and tuning != upstream else world[stage][value]


@pytest.mark.parametrize("depth", [2, 3])
def test_all_public_measurement_outcomes_match_independent_oracle(depth):
    worlds = tuple(product(tuple(permutations(range(3))), repeat=depth))
    for stage in range(depth):
        for x, tuning in product(range(3), repeat=2):
            for value in (None, 0, 1, 2):
                posterior = CategoricalBelief(depth)
                m = Measurement(
                    f"instrument{stage}",
                    {"symbol": SYMBOLS[x], "reading": None if value is None else SYMBOLS[value]},
                    tuning,
                )
                posterior.observe(m)
                compatible = {
                    i for i, w in enumerate(worlds) if oracle(w, stage, x, tuning) == value
                }
                assert posterior.indices == compatible
                for rejected in permutations(range(3)):
                    filtered = CategoricalBelief(depth)
                    filtered.observe(m)
                    filtered.exclude_target(rejected)

                    def target(world):
                        result = []
                        for start in range(3):
                            for law in world:
                                start = law[start]
                            result.append(start)
                        return tuple(result)

                    assert filtered.indices == {
                        i for i in compatible if target(worlds[i]) != rejected
                    }


def test_payload_validation_rejects_unknown_versions_roles_and_private_data():
    valid = {"ontology": FAMILY, "id": "a", "location": "lab", "payload": {"symbol": "ka"}}
    assert DomainArtifact.model_validate(valid).data().symbol == "ka"
    for update in (
        {"ontology": "arbitrary.module"},
        {"version": "domain-v999"},
        {"payload": {"symbol": "ka", "laws": [[0, 1, 2]]}},
        {"payload": {"symbol": 1}},
        {"payload": {"symbol": "water"}},
    ):
        with pytest.raises(ValidationError):
            DomainArtifact.model_validate(valid | update)
    episode = generate_categorical(7).model_dump(mode="json")
    episode["investigation_truth"]["payload"]["laws"].pop()
    with pytest.raises(ValidationError, match="depth"):
        PrivateEpisode.model_validate(episode)


def test_http_privacy_nulls_invalid_action_and_session_isolation():
    episode = generate_categorical(7)
    left, right = Session(episode), Session(episode)
    before = canonical_hash(left.state)
    bad = left.act(0, ConfigureAction(machine="board", settings=(0, 1, 9)))
    assert not bad.ok and canonical_hash(left.state) == before
    response = left.act(0, TakeAction(artifact="S0"))
    assert response.ok and response.performance is None and response.victory_code is None
    assert canonical_hash(right.state) == before == canonical_hash(episode.public.initial_state)
    client = TestClient(create_single_session_app(episode))
    manifest = client.get("/manifest").json()
    text = json.dumps(manifest)
    assert "controller" not in text and "verifier_secret" not in text and '"laws":' not in text
    result = client.post(
        "/action", json={"expected_turn": 0, "action": {"type": "take", "artifact": "S0"}}
    ).json()
    assert "performance" not in result and "victory_code" not in result
    artifact = result["observation"]["carried_artifacts"][0]
    assert "shape" not in artifact and artifact["payload"]["symbol"] == "ka"
    assert result["observation"]["actions_remaining"] is None
    terminal = client.post("/finalize").json()
    assert terminal["performance"]["target_classes_before_first_submission"] is None
    assert terminal["performance"]["budget_remaining"] is None
    assert terminal["performance"]["version"] == "mission-performance-v1"


def test_failed_submission_is_evidence_not_measurement_and_no_signal_is_informative():
    episode = generate_categorical(7)
    session = Session(episode)
    # Any non-permutation target is wrong; it excludes no admitted worlds.
    session.act(0, ConfigureAction(machine="board", settings=(0, 0, 0)))
    result = session.act(1, FinishAction())
    assert result.victory_code is None and result.performance is None
    session.act(2, TakeAction(artifact="S0"))
    # For seed 7 pi0(0)=0, so tuning 1 yields no signal.
    session.act(3, ConfigureAction(machine="instrument1", settings=(1,)))
    out = session.act(4, ProbeAction(machine="instrument1", artifact="S0.3"))
    assert out.events[0]["details"]["result"]["payload"]["signal"] is False
    _, metrics = session.finalize_attempt()
    assert metrics.failed_finishes == 1 and metrics.measurements_used == 1
    assert metrics.informative_measurements == 1


def test_graph_rejects_cycles_unknown_inputs_and_unknown_primitives():
    with pytest.raises(ValueError):
        InvestigationGraph(("x",), (Node("a", "f", ("a",)),), ("a",))
    with pytest.raises(ValueError):
        InvestigationGraph(("x", "x"), (), ("x",))
    graph = InvestigationGraph(("x",), (Node("a", "f", ("x",)),), ("a",))
    with pytest.raises(ValueError):
        graph.evaluate({"x": 0}, {})


def test_runtime_resolution_and_public_projection_do_not_import_inference():
    code = """
import sys
from nexus.models.investigation import InvestigationSpec
from nexus.ontology.catalog import runtime_for
runtime = runtime_for(InvestigationSpec())
assert "nexus.generator.resonance" not in sys.modules
assert "nexus.generator.investigation" not in sys.modules
"""
    # Resolve via a minimal version token to avoid requiring family-specific constructor fields.
    code = code.replace("InvestigationSpec()", "type('Spec', (), {'version': 'scientific-v2'})()")
    subprocess.run([sys.executable, "-c", code], check=True)


def test_loaded_configuration_validation_and_initial_submission_telemetry():
    from nexus.ontology.categorical.runtime import expected

    episode = generate_categorical(7)
    data = episode.model_dump(mode="json")
    data["public"]["initial_state"]["machines"]["instrument1"]["settings"] = [99, 98]
    with pytest.raises(ValidationError, match="initial categorical"):
        PrivateEpisode.model_validate(data)
    episode.public.initial_state.machines["board"].settings = expected(episode)
    episode = PrivateEpisode.model_validate_json(episode.model_dump_json())
    result = Session(episode).act(0, FinishAction())
    assert result.victory_code
    assert result.performance.first_submission_correct
    assert result.performance.failed_finishes == 0


def test_identity_is_keyed_but_world_pairing_does_not_depend_on_secret():
    left = generate_categorical(7, verifier_secret="left")
    right = generate_categorical(7, verifier_secret="right")
    assert left.public.episode_id != right.public.episode_id
    assert left.investigation_truth == right.investigation_truth
    assert (
        left.public.episode_id == generate_categorical(7, verifier_secret="left").public.episode_id
    )
