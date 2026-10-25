"""Evidence witnesses remain prior-only, optional and private."""

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.generator import generate_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.ontology.discovery.policy import public_policy
from nexus.ontology.revision.laws import class_id, compiled, read
from nexus.protocol.operator_witnesses import submission_witnesses
from nexus.protocol.session import Session


def session(seed=1101, *, theory=3):
    return Session(
        generate_episode(
            seed,
            axis_version=2,
            science_family="model-revision-v1",
            theory_level=theory,
            discovery_level=5 if theory else 0,
            planning_level=0,
            resource_pressure=1,
            verifier_secret="witness-private-secret",
        )
    )


def act(s, action):
    response = s.act(s.state.turn, action)
    assert response.ok
    assert "evidence_witnesses" not in response.model_dump_json()
    return response


def install(s, build):
    act(s, ConfigureAction(machine="assembler", settings=build))
    act(s, OperateAction(machine="assembler", artifact="carrier"))


def test_shortest_observed_contradiction_retains_source_turn_and_ignores_future_readings():
    s = session()
    act(s, TakeAction(artifact="carrier"))
    for word in ((0, 1, 1), (1, 0, 0)):
        act(s, ConfigureAction(machine="reader", settings=word))
        act(s, ProbeAction(machine="reader", artifact="carrier"))
    install(s, (0, 8, 3, 8))
    act(s, FinishAction())
    before = canonical_hash(s.state)
    first = s.operator_snapshot()["evidence_witnesses"]
    assert canonical_hash(s.state) == before
    item = first["submissions"][0]
    assert item["classification"] == "contradicted"
    assert item["witness"]["source"] == "reading"
    assert item["witness"]["source_turn"] == 3
    assert item["witness"]["query"] == [0, 1, 1]
    assert item["witness"]["observed"] == [1]
    assert item["witness"]["predicted"] == [0]
    act(s, ConfigureAction(machine="reader", settings=(1, 1)))
    act(s, ProbeAction(machine="reader", artifact="carrier"))
    assert s.operator_snapshot()["evidence_witnesses"] == first


def test_rejected_finish_provenance_and_repeated_equivalent_build():
    s = session(5866)
    act(s, TakeAction(artifact="carrier"))
    provisional = s.episode.public.investigation.data().provisional
    install(s, provisional)
    act(s, FinishAction())
    act(s, FinishAction())
    first, second = s.operator_snapshot()["evidence_witnesses"]["submissions"]
    assert first["classification"] == "compatible"
    assert first["witness"]["kind"] == "unresolved_alternative"
    assert second["classification"] == "contradicted" and second["repeated_build"]
    assert second["witness"]["kind"] == "rejection_contradiction"
    assert second["witness"]["source_turn"] == first["turn"]
    assert first["previous_rejected_equivalent_turn"] is None
    assert second["previous_rejected_equivalent_turn"] == first["turn"]


@pytest.mark.parametrize("observe_conflict", [False, True])
def test_different_wiring_repeats_rejected_behavior_even_with_reading_conflict(observe_conflict):
    from nexus.protocol.operator_summary import compact_summary

    s = session(6464)
    first_build, equivalent = (3, 4, 8, 10), (3, 4, 11, 7)
    assert first_build != equivalent and class_id(first_build) == class_id(equivalent)
    act(s, TakeAction(artifact="carrier"))
    install(s, first_build)
    rejected = act(s, FinishAction())
    assert rejected.victory_code is None
    if observe_conflict:
        from nexus.ontology.revision.laws import QUERIES

        truth = s.episode.investigation_truth.data().program
        word = next(w for w in QUERIES if read(truth, w) != read(first_build, w))
        act(s, ConfigureAction(machine="reader", settings=word))
        act(s, ProbeAction(machine="reader", artifact="carrier"))
    install(s, equivalent)
    act(s, FinishAction())
    snapshot = s.operator_snapshot()
    report = snapshot["evidence_witnesses"]
    assert report["version"] == "evidence-witnesses-v2"
    assert report["decision_equivalence_available"]
    first, second = report["submissions"]
    assert second["classification"] == "contradicted"
    assert not second["repeated_build"]
    assert second["previous_rejected_equivalent_turn"] == first["turn"]
    assert second["witness"]["kind"] == (
        "observation_contradiction" if observe_conflict else "rejection_contradiction"
    )
    summary = compact_summary(snapshot, s.trace)
    assert summary["repeated_build_submissions"] == 0
    assert summary["rejected_equivalent_submissions"] == 1


def test_equivalence_is_optional_and_different_behavior_is_not_a_repeat(monkeypatch):
    from nexus.ontology.revision import runtime
    from nexus.protocol.operator_summary import compact_summary

    s = session(5866)
    act(s, FinishAction())  # Ineligible: cannot exclude an unsubmitted program.
    act(s, TakeAction(artifact="carrier"))
    install(s, s.episode.public.investigation.data().provisional)
    act(s, FinishAction())
    install(s, s.episode.investigation_truth.data().program)
    assert act(s, FinishAction()).victory_code
    snapshot = s.operator_snapshot()
    assert all(
        x["previous_rejected_equivalent_turn"] is None
        for x in snapshot["evidence_witnesses"]["submissions"]
    )
    assert compact_summary(snapshot, s.trace)["rejected_equivalent_submissions"] == 0
    monkeypatch.delattr(runtime, "decision_equivalence_key")
    snapshot = s.operator_snapshot()
    assert not snapshot["evidence_witnesses"]["decision_equivalence_available"]
    assert compact_summary(snapshot, s.trace)["rejected_equivalent_submissions"] is None


def test_declared_equivalence_cannot_silently_return_an_unavailable_key(monkeypatch):
    from nexus.ontology.revision import runtime

    s = session(5866)
    act(s, TakeAction(artifact="carrier"))
    install(s, s.episode.public.investigation.data().provisional)
    act(s, FinishAction())
    monkeypatch.setattr(runtime, "decision_equivalence_key", lambda spec, decision: None)
    with pytest.raises(ValueError, match="null key"):
        submission_witnesses(s.episode.public, s.trace)


def test_compatible_win_is_not_retroactively_supported_and_alternative_is_a_survivor():
    s = session(5866)
    act(s, TakeAction(artifact="carrier"))
    build = s.episode.investigation_truth.data().program
    install(s, build)
    result = act(s, FinishAction())
    assert result.victory_code
    report = submission_witnesses(s.episode.public, s.trace)
    item = report.submissions[0]
    assert item.classification == "compatible"
    witness = item.witness
    assert (
        tuple(compiled().rows[class_id(witness.alternative)][:2])
        == s.episode.public.investigation.data().archive
    )
    assert read(build, witness.query) != read(witness.alternative, witness.query)
    assert "witness-private-secret" not in report.model_dump_json()
    assert result.victory_code not in report.model_dump_json()


@pytest.mark.parametrize("theory", [0, 3])
def test_supported_finish_has_no_witness(theory):
    s = session(theory=theory)
    assert public_policy(s, s.episode.public.evidence_files).victory_code
    report = s.operator_snapshot()["evidence_witnesses"]
    item = report["submissions"][0]
    assert item["classification"] == "guaranteed" and item["witness"] is None
    point = report["first_supported_decision"]
    assert point is not None and point["turn"] < item["turn"]
    expected_hash = (
        canonical_hash(s.episode.public.initial_state)
        if point["turn"] == 0
        else s.trace[point["turn"] - 1].after_hash
    )
    assert point["state_sha256"] == expected_hash
    assert read(tuple(point["decision"]), (0, 1, 1)) == read(
        s.episode.investigation_truth.data().program, (0, 1, 1)
    )


def test_ineligible_and_other_families_remain_well_defined():
    s = session()
    act(s, FinishAction())
    item = s.operator_snapshot()["evidence_witnesses"]["submissions"][0]
    assert item["classification"] == "ineligible" and item["witness"] is None
    legacy = Session(generate_episode(17))
    assert legacy.operator_snapshot()["evidence_witnesses"] is None


def test_archive_and_disclosed_construction_are_distinct_sources():
    s = session(5866)
    act(s, TakeAction(artifact="carrier"))
    install(s, (0, 0, 0, 0))
    act(s, FinishAction())
    assert (
        s.operator_snapshot()["evidence_witnesses"]["submissions"][0]["witness"]["source"]
        == "archive"
    )
    s = session(5866, theory=0)
    act(s, TakeAction(artifact="carrier"))
    install(s, s.episode.public.investigation.data().provisional)
    act(s, FinishAction())
    assert (
        s.operator_snapshot()["evidence_witnesses"]["submissions"][0]["witness"]["source"]
        == "disclosed_construction"
    )
