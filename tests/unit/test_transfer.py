"""Independent arithmetic, shortcut rivals, exact mission and canonical actions."""

import json
import runpy
from pathlib import Path

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.inference import Measurement
from nexus.ontology.transfer import runtime
from nexus.ontology.transfer.inference import Belief
from nexus.ontology.transfer.laws import PROGRAMS, QUERIES, accepted, displayed, physical, targets
from nexus.ontology.transfer.policy import public_policy
from nexus.ontology.transfer.reference import load
from nexus.protocol.session import Session

ORACLE = runpy.run_path(str(Path(__file__).parents[2] / "scripts/poc_evidence_transfer.py"))


def episode(seed=3550, *, coupled=True, control=False, planning=0, profile="standard"):
    return generate_episode(
        seed,
        axis_version=2,
        science_family="coupled-evidence-v1" if coupled else "coupled-transfer-v1",
        theory_level=0 if control else 3,
        discovery_level=0 if control else 5,
        planning_level=planning,
        resource_pressure=1,
        budget_profile=profile,
        verifier_secret="transfer-test",
    )


def act(session, action):
    result = session.act(expected_turn=session.state.turn, action=action)
    assert result.ok, result.message
    return result


@pytest.mark.slow
def test_exhaustive_independent_physics_observations_and_equivalence():
    assert PROGRAMS == ORACLE["programs"]() and QUERIES == ORACLE["conditions"]()
    labels = {}
    independent_targets = []
    for i, program in enumerate(PROGRAMS):
        row = bytes(ORACLE["scalar"](program, q) for q in QUERIES)
        independent_targets.append(labels.setdefault(row, i))
        for q, value in zip(QUERIES, row):
            assert physical(program, q) == value
            for offset in range(3):
                e = ORACLE["reader"](program, offset, q)
                assert displayed(program, offset, q, "reference", True) == e
                assert displayed(program, offset, q, "survey", True) == (value + e) % 3
    assert tuple(independent_targets) == load()["targets"] == targets()
    assert len(labels) == 5016


@pytest.mark.parametrize("coupled", [False, True])
def test_every_public_policy_branch_against_independent_oracle(coupled):
    data = load()["coupled" if coupled else "calibrated"]
    seen = set()
    maximum = 0
    for offset in range(3 if coupled else 1):
        for i, program in enumerate(PROGRAMS):
            node, readings = 0, 0
            while node >= 0:
                seen.add(node)
                query, *children = data["nodes"][node]
                material, index = divmod(query, len(QUERIES))
                q = QUERIES[index]
                value = 0 if material else ORACLE["scalar"](program, q)
                if coupled:
                    value = (value + ORACLE["reader"](program, offset, q)) % 3
                node = children[value]
                assert node is not None
                readings += 1
            assert load()["targets"][i] == -node - 1
            maximum = max(maximum, readings)
    assert len(seen) == len(data["nodes"])
    assert maximum == data["readings"] == (10 if coupled else 9)


@pytest.mark.parametrize("coupled", [False, True])
@pytest.mark.parametrize(
    "control,planning,profile",
    [(False, 0, "standard"), (False, 1, "diagnostic-plus6"), (True, 1, "standard")],
)
def test_live_policy_replay_terminal_diagnostics(coupled, control, planning, profile, caplog):
    ep = episode(coupled=coupled, control=control, planning=planning, profile=profile)
    session = Session(ep)
    with caplog.at_level("INFO", logger="nexus.diagnostics"):
        result = public_policy(session, ep.public.evidence_files)
    assert result.victory_code
    assert result.current_turn <= ep.generation_metadata.guaranteed_policy_action_count
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert "transfer_posterior" in caplog.text
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert qualify_episode(ep).passed


def test_paired_truth_budget_and_control_contract():
    left = episode()
    right = episode(coupled=False)
    generous = episode(profile="diagnostic-plus6")
    assert (
        left.investigation_truth.payload["program"] == right.investigation_truth.payload["program"]
    )
    assert left.investigation_truth == generous.investigation_truth
    assert left.public.evidence_files == generous.public.evidence_files
    assert generous.generation_metadata.action_budget == left.generation_metadata.action_budget + 6
    control = episode(control=True)
    assert control.public.investigation.data().resolved == runtime.expected(control)
    assert Belief(control.public.investigation.data()).counts()[1] == 1
    for name in (
        "observation_model",
        "reference_scope",
        "primitives_in_selector_order",
        "graphs_in_selector_order",
        "mission",
    ):
        assert name in json.loads(left.public.evidence_files["theory.json"])


def test_raw_probe_preparation_immutability_invalid_actions_and_actual_application():
    ep = episode()
    session = Session(ep)
    specimen = act(session, TakeAction(artifact="stock")).events[0]["details"]["artifact"]
    act(session, TakeAction(artifact="seal"))
    initial = session.state.model_dump(mode="json")
    bad = session.act(
        expected_turn=session.state.turn,
        action=ConfigureAction(machine="doser", settings=(0, 0, 0, 0, 0, 0, 0)),
    )
    assert not bad.ok and session.state.model_dump(mode="json") == initial
    setting = (1, 2, 1, 2, 1, 1)
    act(session, ConfigureAction(machine="stage", settings=setting))
    act(session, ProbeAction(machine="stage", artifact=specimen))
    assert session.state.artifacts[specimen].data().settings == (0,) * 6
    act(session, OperateAction(machine="stage", artifact=specimen))
    before = session.state.artifacts[specimen].model_dump(mode="json")
    result = act(session, ProbeAction(machine="sensor", artifact=specimen))
    payload = next(
        e["details"]["result"]["payload"] for e in result.events if "result" in e["details"]
    )
    truth = ep.investigation_truth.data()
    assert payload["reading"] == displayed(
        truth.program, truth.reader_offset, setting, "survey", True
    )
    assert set(payload) == {"material", "settings", "reading", "doses"}
    assert session.state.artifacts[specimen].model_dump(mode="json") == before
    assert result.performance is None
    act(session, OperateAction(machine="sensor", artifact=specimen))
    act(session, OperateAction(machine="stage", artifact=specimen))
    assert session.state.artifacts[specimen].data().reading is None
    act(session, ConfigureAction(machine="doser", settings=runtime.expected(ep)))
    act(session, ProbeAction(machine="doser", artifact="seal"))
    assert not act(session, FinishAction()).victory_code
    act(session, OperateAction(machine="doser", artifact="seal"))
    act(session, DropAction(artifact="seal"))
    assert not act(session, FinishAction()).victory_code
    act(session, TakeAction(artifact="seal"))
    assert act(session, FinishAction()).victory_code


def test_structural_rivals_posterior_and_behavioral_acceptance():
    left, right = PROGRAMS[1183 * 3 + 1], PROGRAMS[1229 * 3 + 1]
    assert not accepted(left, right)
    assert all(
        displayed(left, 2, q, "survey", True) == displayed(right, 2, q, "survey", True)
        for q in QUERIES
    )
    assert any(
        displayed(left, 2, q, "reference", True) != displayed(right, 2, q, "reference", True)
        for q in QUERIES
    )
    belief = Belief(episode().public.investigation.data())
    for q in QUERIES:
        belief.observe(
            Measurement(
                "sensor",
                {
                    "reading": displayed(left, 2, q, "survey", True),
                    "material": "survey",
                    "settings": q,
                },
            )
        )
    assert (
        not belief.common_decisions()
        and belief.accepting_count(left)
        and belief.accepting_count(right)
    )
    for q in QUERIES:
        belief.observe(
            Measurement(
                "sensor",
                {
                    "reading": displayed(left, 2, q, "reference", True),
                    "material": "reference",
                    "settings": q,
                },
            )
        )
    assert belief.supports(left) and not belief.supports(right)
    equivalent = next(i for i, t in enumerate(targets()) if i != t)
    assert accepted(PROGRAMS[equivalent], PROGRAMS[targets()[equivalent]])
    belief.exclude_target(left)
    assert belief.counts() == (0, 0)


@pytest.mark.parametrize("mutation", ["evidence", "truth", "budget", "family"])
def test_tampered_compiled_contract_rejected(mutation):
    raw = episode().model_dump(mode="json")
    if mutation == "evidence":
        raw["public"]["evidence_files"]["apparatus.txt"] += " hidden hint"
    elif mutation == "truth":
        raw["investigation_truth"]["payload"]["reader_offset"] = 2
    elif mutation == "budget":
        raw["generation_metadata"]["action_budget"] += 1
    else:
        raw["public"]["investigation"]["payload"]["coupled"] = False
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(raw)


def test_actual_channel_ablations_are_distinct_from_physical_only():
    from nexus.evaluation.transfer import Cell, fixture_checks, restricted_closures

    calibrated = Cell(id="a", seed=3550, family="coupled-transfer-v1", passive_rival=3562)
    coupled = Cell(
        id="b", seed=3550, family="coupled-evidence-v1", survey_rival=3688, passive_rival=3562
    )
    assert all(fixture_checks(calibrated).values()) and all(fixture_checks(coupled).values())
    assert (
        restricted_closures(calibrated)["all_passive_observations"]["physical_behavior_classes"] > 1
    )
    assert (
        restricted_closures(coupled)["all_passive_observations"]["physical_behavior_classes"] == 1
    )
    with pytest.raises(ValueError, match="fixture claims fail"):
        fixture_checks(Cell(id="bad", seed=3550, family="coupled-evidence-v1", survey_rival=3550))


def test_policy_asset_is_immutable_and_stale_semantics_fail_closed(monkeypatch):
    from nexus.ontology.transfer import reference

    with pytest.raises(TypeError):
        load()["calibrated"]["nodes"][0][0] = 1
    reference.load.cache_clear()
    with monkeypatch.context() as patch:
        patch.setattr(reference, "semantic_digest", lambda: "stale")
        with pytest.raises(ValueError, match="stale transfer reference"):
            reference.load()
    reference.load.cache_clear()
    assert reference.load()["version"] == "transfer-reference-v1"


def test_independent_proof_rejects_disabled_assertions(tmp_path):
    import subprocess
    import sys

    output = tmp_path / "proof.json"
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            str(Path(__file__).parents[2] / "scripts/poc_evidence_transfer.py"),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0 and "requires Python assertions" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("fault", ["hash", "semantics", "truncated", "overlong", "partition"])
def test_observation_asset_rejects_corruption_and_staleness(monkeypatch, tmp_path, fault):
    import base64
    import hashlib
    import zlib

    from nexus.ontology.transfer import observations, observations_identity

    original = Path(observations.__file__).with_name("observations.json")
    data = json.loads(original.read_bytes())
    if fault == "semantics":
        data["semantic_digest"] = "stale"
    elif fault in ("truncated", "overlong", "partition"):
        decoded = zlib.decompress(base64.b64decode(data["data"]))
        if fault == "truncated":
            decoded = decoded[:-1]
        elif fault == "overlong":
            decoded += b"x"
        else:
            decoded = bytes(len(decoded))
        data["data"] = base64.b64encode(zlib.compress(decoded)).decode()
    raw = json.dumps(data).encode()
    (tmp_path / "observations.json").write_bytes(raw)
    observations.load.cache_clear()
    try:
        with monkeypatch.context() as patch:
            patch.setattr(observations, "files", lambda package: tmp_path)
            if fault != "hash":
                patch.setattr(observations_identity, "SHA256", hashlib.sha256(raw).hexdigest())
            with pytest.raises(ValueError, match="transfer observation"):
                observations.load()
    finally:
        observations.load.cache_clear()
    with pytest.raises(TypeError):
        observations.load()[0][0][0] = 0


def test_offline_policy_compiler_does_not_require_existing_policy_asset(monkeypatch):
    from nexus.ontology.transfer import reference

    compiler = runpy.run_path(
        str(Path(__file__).parents[2] / "scripts/compile_transfer_reference.py")
    )

    def missing_policy():
        raise FileNotFoundError("no compiled policy yet")

    monkeypatch.setattr(reference, "load", missing_policy)
    # A one-behavior domain keeps this regression focused on bootstrap independence.
    from nexus.ontology.transfer import tables

    monkeypatch.setattr(tables, "load_reference", missing_policy)
    table = tables.assemble_tables(False, (0,) * len(PROGRAMS))
    assert table.common(table.full)
    monkeypatch.setitem(compiler["tree"].__globals__, "targets", lambda: (0,) * len(PROGRAMS))
    assert compiler["tree"](False) == {"readings": 0, "nodes": []}
