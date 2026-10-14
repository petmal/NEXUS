"""Factored coverage of every science-bearing state/control class.

The complete-state induction and administrative action partition are documented
in repair-live-conformance.md. These tests check its finite component premises;
they do not claim enumeration of the inventory/history cross-product.
"""

from dataclasses import replace
from itertools import product

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
)
from nexus.models.domain import DomainArtifact
from nexus.models.world import INVENTORY, Room
from nexus.ontology.repair.generation import generate_repair
from nexus.ontology.repair.laws import response, solution, transform, worlds
from nexus.ontology.repair.policy import check_program, execute, witness
from nexus.ontology.repair.qualification import qualify_repair
from nexus.ontology.repair.schema import FAMILY, Specimen
from nexus.protocol.http import create_app
from nexus.protocol.session import Session


def test_all_preparation_classes_and_legal_controls_obey_public_state_factorization():
    # Vary every attainable orientation/charge class, both materials, and every
    # legal setting. Cached readings are erased, never recomputed by preparation.
    samples = [Specimen()]
    samples += [
        Specimen(context=(mode, x), charged=charged, reading=(6,), instrument="reference")
        for mode, x, charged in product((0, 1), range(7), (False, True))
    ]
    samples += [Specimen(material="seal", doses=dose) for dose in product(range(7), repeat=4)]
    for sample in samples:
        for machine, settings in [("stage", (m, x)) for m, x in product((0, 1), range(7))] + [
            ("coupler", None)
        ]:
            result = transform(worlds()[0], sample, machine, settings)
            assert result.reading is None and result.instrument is None
            assert result.material == sample.material and result.doses == sample.doses
            if sample.material == "seal":
                assert result.context is None and not result.charged
            elif machine == "stage":
                assert result.context == settings and not result.charged
            else:
                assert result.context == sample.context and result.charged == (
                    sample.context is not None
                )
    for dose in product(range(7), repeat=4):
        for sample in (
            Specimen(),
            Specimen(context=(1, 6), charged=True),
            Specimen(material="seal"),
        ):
            result = transform(worlds()[-1], sample, "doser", dose)
            assert result.doses == (dose if sample.material == "seal" else None)
            assert (result.context, result.charged) == (sample.context, sample.charged)


def test_every_hidden_response_class_matches_complete_payload_and_engine_commit_semantics():
    # Existing pure test covers all 7,203 truths x 14 coordinates arithmetically.
    # Here all 29 survey preparation classes exercise actual operate/probe paths.
    episode = generate_repair(3217, planning_level=0)
    world = episode.investigation_truth.data()
    samples = (
        [Specimen()]
        + [
            Specimen(context=(m, x), charged=c)
            for m, x, c in product((0, 1), range(7), (False, True))
        ]
        + [Specimen(material="seal")]
    )
    for sample, machine, action_type in product(
        samples, ("reference", "reader"), (ProbeAction, OperateAction)
    ):
        state = episode.public.initial_state.model_copy(deep=True)
        state.artifacts["test"] = DomainArtifact(
            ontology=FAMILY, id="test", location=INVENTORY, payload=sample.model_dump(mode="json")
        )
        before = canonical_hash(state)
        result = step(state, action_type(machine=machine, artifact="test"), episode)
        expected = sample.model_dump(mode="json")
        reading = None
        if sample.material == "survey":
            if machine == "reference":
                reading = (world.a,)
            elif sample.charged:
                reading = response(world, sample.context)
        expected.update(reading=None if reading is None else list(reading), instrument=machine)
        assert result.ok and result.state.turn == 1
        assert result.events[0].details["result"]["payload"] == expected
        assert canonical_hash(state) == before
        assert result.state.artifacts["test"].payload == (
            sample.model_dump(mode="json") if action_type is ProbeAction else expected
        )


def test_every_raw_dose_uses_applied_key_and_eligibility_not_apparatus_settings():
    episode = generate_repair(42, planning_level=0)
    w = episode.investigation_truth.data()
    good = solution(w.a, w.b, w.c, w.degree)
    for dose in product(range(7), repeat=4):
        for carried in (False, True):
            state = episode.public.initial_state.model_copy(deep=True)
            state.artifacts["seal"].location = INVENTORY if carried else "array"
            state.artifacts["seal"].payload = Specimen(material="seal", doses=dose).model_dump(
                mode="json"
            )
            state.machines["doser"].settings = good  # Never changes acceptance by itself.
            result = step(state, FinishAction(), episode)
            assert bool(result.victory_code) == (carried and dose == good)
            if not result.victory_code:
                assert result.message == "" and result.events[0].type == "finish_rejected"


def test_ineligible_finish_does_not_exclude_a_correct_applied_dose():
    episode = generate_repair(42, planning_level=0)
    w = episode.investigation_truth.data()
    session = Session(episode)
    for action in (
        TakeAction(artifact="seal"),
        ConfigureAction(machine="doser", settings=solution(w.a, w.b, w.c, w.degree)),
        OperateAction(machine="doser", artifact="seal"),
        DropAction(artifact="seal"),
        FinishAction(),
        TakeAction(artifact="seal"),
        TakeAction(artifact="stock"),
        ProbeAction(machine="reference", artifact="stock.7"),
        ConfigureAction(machine="stage", settings=(0, w.a)),
        OperateAction(machine="stage", artifact="stock.7"),
        OperateAction(machine="coupler", artifact="stock.7"),
        ProbeAction(machine="reader", artifact="stock.7"),
        ConfigureAction(machine="stage", settings=(1, w.b)),
        OperateAction(machine="stage", artifact="stock.7"),
        OperateAction(machine="coupler", artifact="stock.7"),
        ProbeAction(machine="reader", artifact="stock.7"),
        FinishAction(),
    ):
        result = session.act(session.status().turn, action)
        assert result.ok
    assert result.victory_code and result.performance.failed_finishes == 1
    assert result.performance.final_submission_correct
    assert result.performance.target_reducing_measurements == 3


def test_restart_surface_and_complete_public_template_mutations_fail_closed():
    base = generate_repair(42, planning_level=0)
    with pytest.raises(ValueError, match="non-resettable"):
        create_app(base)
    changed = base.model_copy(deep=True)
    changed.public.rooms["array"] = Room(id="hint", label="Material stores")
    assert not qualify_repair(changed).passed


def test_literal_program_rejects_false_round_claims_commands_and_missing_response_branches():
    program = witness(0)
    assert program.feedback_rounds == 3 and program.action_upper == 14
    with pytest.raises(ValueError, match="scope"):
        check_program(replace(program, feedback_rounds=2))
    with pytest.raises(ValueError, match="command"):
        check_program(
            replace(program, root=replace(program.root, commands=(len(program.actions),)))
        )
    missing = replace(program, root=replace(program.root, branches=program.root.branches[1:]))
    with pytest.raises(ValueError, match="no branch"):
        execute(Session(generate_repair(0, planning_level=0)), missing)
