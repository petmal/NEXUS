"""All-history equivalence, conservative feedback and honest qualification bounds."""

import json
from pathlib import Path

import pytest

from nexus.ontology.coupled_memory import laws
from nexus.ontology.coupled_memory.inference import Belief
from nexus.ontology.coupled_memory.proof import oracle, predictive_witness, prove
from nexus.ontology.inference import Measurement


def test_complete_proof_and_counterfactual_bandwidth_controls():
    p = prove()
    assert p["all_legal_states_checked"] == 384 * 135
    assert p["behavior_classes"] == 336
    assert p["adaptive_reading_lower"] == p["adaptive_reading_upper"] == 6
    assert set(map(len, p["certificates"])) == {3}
    assert (p["fixed_panel_lower"], p["fixed_panel_upper"]) == (6, 9)
    assert not p["fixed_panel_optimality_proven"] and not p["deep_tier_admitted"]
    assert p["oracle_ablations"]["known_dynamics"]["bounds"] == [(2, 2)]
    assert p["oracle_ablations"]["known_encoder"]["bounds"] == [(4, 4)]
    assert p["bandwidth_controls"]["2"]["reading_upper"] == 9
    assert p["bandwidth_controls"]["5"]["reading_upper"] == 4
    assert p["single_queries_eliminating_no_encoder"] == 120
    assert p["single_queries_with_encoder_frequency_signal"] == 120
    assert p["behavior_classes_spanning_encoders"] == 48
    assert sum(w is not None for w in p["feedback_ablations"]["memory_to_transfer"]) == 372
    assert all(p["feedback_ablations"]["material_to_memory"])
    # Exported decision tree and every certificate must work, independent of choose().
    for i, program in enumerate(laws.PROGRAMS):
        world = laws.Truth(program=program)
        b = Belief(laws.specification(world, 3, 4))
        node = p["decision_tree"]
        while "query" in node:
            query = tuple(node["query"])
            value = laws.read(program, query)
            b.observe(Measurement("reader", {"query": query, "values": value}))
            node = node["answers"][str(value[0])]
        assert b.supports(tuple(node["build"]))
        b = Belief(laws.specification(world, 3, 4))
        for query in p["certificates"][i]:
            b.observe(Measurement("reader", {"query": query, "values": laws.read(program, query)}))
        assert b.supports(program)


@pytest.mark.parametrize("defect", ["loss", "new_h"])
def test_independent_proof_detects_conservation_and_update_order_mutations(monkeypatch, defect):
    original = laws.advance

    def broken(program, state, pulse):
        new = list(original(program, state, pulse))
        if defect == "loss":
            new[0] -= 1
        else:
            new[4] = (new[4] + new[3] - state[3]) % 3
        return tuple(new)

    prove.cache_clear()
    try:
        monkeypatch.setattr(laws, "advance", broken)
        with pytest.raises(ValueError, match="conformance"):
            prove()
    finally:
        prove.cache_clear()


def test_equivalent_encoder_spellings_are_accepted_but_partial_transcripts_are_not():
    table, rows, _ = laws.tables()
    pair = next(
        (i, j)
        for i in range(len(rows))
        for j in range(i)
        if rows[i] == rows[j] and laws.PROGRAMS[i][4:] != laws.PROGRAMS[j][4:]
    )
    i, j = pair
    assert laws.accepted(laws.selection(i), laws.PROGRAMS[j])
    i, j = next(
        (i, j)
        for i in range(len(rows))
        for j in range(i)
        if rows[i][:12] == rows[j][:12] and rows[i] != rows[j]
    )
    assert not laws.equivalent(laws.PROGRAMS[i], laws.PROGRAMS[j])
    belief = Belief(laws.specification(laws.selection(i), 3, 4))
    belief.exclude_target(laws.PROGRAMS[j])
    assert belief.mask == ((1 << len(rows)) - 1) & ~table.accepting[j]


def test_same_current_display_can_require_different_future_predictions():
    program = laws.selection(95).program
    witness = predictive_witness(program)
    assert witness and witness["suffix"]
    a, b = map(tuple, witness["histories"])
    assert laws.read(program, a) == laws.read(program, b)
    suffix = tuple(witness["suffix"])
    assert laws.read(program, a + suffix) != laws.read(program, b + suffix)
    # The hidden state stays conservative throughout both histories.
    for word in (a + suffix, b + suffix):
        state = laws.INITIAL
        for pulse in word:
            state = oracle(program, state, pulse)
            assert sum(state[:3]) == 4 and min(state[:3]) >= 0
            assert all(v in range(3) for v in state[3:])


def test_paired_matrix_and_inflated_claims_fail_closed(tmp_path):
    from nexus.evaluation.coupled_memory import Pilot, preflight

    path = Path(__file__).parents[2] / "docs/coupled-memory-matrix.json"
    raw = json.loads(path.read_text())
    report = preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert report["status"] == "passed" and len(report["cells"]) == 10
    raw["runs"][3]["expected_certificate_lower"] = 4
    raw["runs"][3]["expected_certificate_upper"] = 4
    with pytest.raises(ValueError, match="failed checks"):
        preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "blocked"


def test_t2_blind_enumeration_is_a_real_legal_shortcut():
    from nexus.generator import generate_episode
    from nexus.models.actions import ConfigureAction, FinishAction, OperateAction, TakeAction
    from nexus.protocol.session import Session

    ep = generate_episode(
        95,
        axis_version=2,
        science_family="coupled-memory-v1",
        theory_level=2,
        discovery_level=4,
        planning_level=0,
        resource_pressure=1,
    )
    session = Session(ep)

    def act(action):
        result = session.act(session.state.turn, action)
        assert result.ok
        return result

    act(TakeAction(artifact="carrier"))
    disclosed = ep.public.investigation.data().known
    for build in laws.PROGRAMS:
        if build[:4] != disclosed:
            continue
        act(ConfigureAction(machine="assembler", settings=build))
        act(OperateAction(machine="assembler", artifact="carrier"))
        result = act(FinishAction())
        if result.victory_code:
            break
    assert result.victory_code and result.current_turn <= 25
    assert result.performance.measurements_used == 0


def test_acceptance_rejects_difference_beyond_reader_horizon(monkeypatch):
    left, right = laws.PROGRAMS[:2]

    def transition(program, state, pulse):
        return (min(state[0] + 1, 5),)

    def display(program, state):
        return int(program == right and state[0] == 5)

    laws.equivalent.cache_clear()
    try:
        with monkeypatch.context() as patch:
            patch.setattr(laws, "INITIAL", (0,))
            patch.setattr(laws, "advance", transition)
            patch.setattr(laws, "display", display)
            assert all(laws.read(left, q) == laws.read(right, q) for q in laws.QUERIES)
            assert not laws.accepted(laws.Truth(program=left), right)
    finally:
        laws.equivalent.cache_clear()


def test_every_legal_reader_setting_has_same_probe_and_operate_information():
    from nexus.engine.canonical import canonical_hash
    from nexus.engine.replay import replay
    from nexus.generator import generate_episode
    from nexus.models.actions import ConfigureAction, OperateAction, ProbeAction, TakeAction
    from nexus.protocol.session import Session

    ep = generate_episode(
        95,
        axis_version=2,
        science_family="coupled-memory-v1",
        theory_level=3,
        discovery_level=4,
        planning_level=0,
        resource_pressure=0,
    )
    s = Session(ep)
    assert s.act(0, TakeAction(artifact="carrier")).ok
    for query in laws.QUERIES:
        assert s.act(s.state.turn, ConfigureAction(machine="reader", settings=query)).ok
        before = s.state.artifacts["carrier"].model_dump()
        for action_type in (ProbeAction, OperateAction):
            result = s.act(s.state.turn, action_type(machine="reader", artifact="carrier"))
            assert result.ok and result.performance is None
            reading = next(
                e["details"]["result"]["payload"]["reading"]
                for e in result.events
                if "result" in e["details"]
            )
            assert tuple(reading["values"]) == laws.read(
                ep.investigation_truth.data().program, query
            )
            if action_type is ProbeAction:
                assert s.state.artifacts["carrier"].model_dump() == before
    assert canonical_hash(replay(ep, s.trace)) == canonical_hash(s.state)


def test_matrix_blocks_missing_observable_feedback(tmp_path):
    from nexus.evaluation.coupled_memory import Pilot, preflight
    from nexus.ontology.coupled_memory.proof import world_audit

    p = prove()
    missing = next(
        i for i, v in enumerate(p["feedback_ablations"]["memory_to_transfer"]) if v is None
    )
    world = laws.selection(missing)
    detail = world_audit(laws.specification(world, 3, 4), world)
    raw = json.loads((Path(__file__).parents[2] / "docs/coupled-memory-matrix.json").read_text())
    raw["runs"][5].update(seed=missing, expected_policy_readings=detail["public_policy_readings"])
    with pytest.raises(ValueError, match="bidirectional_feedback_observable.*False"):
        preflight(Pilot.model_validate(raw), tmp_path / "report.json")
    assert json.loads((tmp_path / "report.json").read_text())["status"] == "blocked"


def test_exported_mindtrial_inputs_match_matrix():
    import re

    root = Path(__file__).parents[2]
    rows = json.loads((root / "docs/coupled-memory-matrix.json").read_text())["runs"]
    text = (root / "examples/mindtrial/nexus-coupled-memory-tasks.yaml").read_text()
    blocks = text.split("service-inputs:")[1:]
    assert len(blocks) == len(rows) == 10
    for block, row in zip(blocks, rows):
        for field, value in {
            "science-family": row["family"],
            "seed": row["seed"],
            "theory-level": row["theory"],
            "discovery-level": row["discovery"],
            "resource-pressure": row["resource"],
            "planning-level": 0,
        }.items():
            found = re.search(r"^\s+" + field + r": ['\"]?([^\s'\"]+)", block, re.MULTILINE)
            assert found and found.group(1) == str(value)
    config = (root / "examples/mindtrial/nexus-coupled-memory-config.yaml").read_text()
    assert "./nexus-coupled-memory-tasks.yaml" in config
    assert re.findall(r"^\s+image: (\S+)", config, re.MULTILINE) == ["nexus:coupled-memory-v1"] * 3
