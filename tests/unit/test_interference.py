"""Public multi-write semantics, exact proofs, budgets and private contract checks."""

import json

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    FinishAction,
    OperateAction,
    ProbeAction,
    TakeAction,
    WaitAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.inference import Measurement
from nexus.ontology.interference.generation import selection
from nexus.ontology.interference.inference import Belief
from nexus.ontology.interference.laws import step
from nexus.ontology.interference.planner import (
    actions_for,
    bank_contiguous_distances,
    minimum_goal_breaks,
    optimal,
)
from nexus.ontology.interference.policy import public_policy
from nexus.ontology.interference.proof import (
    independent_bank_minima,
    scalar_cost,
    scalar_minimum_goal_breaks,
)
from nexus.ontology.interference.schema import FAMILY, GenerationOptions, Specimen, Structure, Truth
from nexus.protocol.session import Session


def episode(seed=67, horizon="short", coupling="coupled", resource=2):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=0,
        discovery_level=0,
        planning_level=0,
        resource_pressure=resource,
        ontology_options={"horizon": horizon, "coupling": coupling},
        verifier_secret="interference-test",
    )


@pytest.mark.parametrize("seed", [67, 79, 101, 103])
def test_seed_matched_targets_extend_horizon_and_coupled_optima_require_revisits(seed):
    specs = {
        (h, c): episode(seed, h, c).public.investigation.data()
        for h in ("short", "long")
        for c in ("independent", "coupled")
    }
    assert len({s.resolved for s in specs.values()}) == 1
    for horizon in ("short", "long"):
        independent, coupled = (specs[horizon, c] for c in ("independent", "coupled"))
        assert independent.target == coupled.target
        assert optimal(independent).actions == sum(independent_bank_minima(independent)) + 2
        for spec in (independent, coupled):
            assert optimal(spec).actions == scalar_cost(spec) + 2
        baseline = scalar_cost(coupled, "bank_contiguous")
        assert baseline is None or optimal(coupled).actions - 2 < baseline
    assert 12 <= optimal(specs["short", "coupled"]).actions - 2 <= 20
    assert 30 <= optimal(specs["long", "coupled"]).actions - 2 <= 48
    for coupling, gap in (("independent", 4), ("coupled", 10)):
        assert (
            optimal(specs["long", coupling]).actions
            >= optimal(specs["short", coupling]).actions + gap
        )
    assert 1 <= selection(seed).attempt <= 32


@pytest.mark.parametrize("horizon", ["short", "long"])
@pytest.mark.parametrize("coupling", ["independent", "coupled"])
def test_independent_coordinate_regression_proof_and_restricted_cost(horizon, coupling):
    from nexus.ontology.interference.laws import encode

    spec = episode(101, horizon, coupling).public.investigation.data()
    assert minimum_goal_breaks(spec) == scalar_minimum_goal_breaks(spec)
    if coupling == "coupled":
        assert minimum_goal_breaks(spec) > 0 and scalar_cost(spec, "goal_preserving") is None
    assert bank_contiguous_distances(spec.resolved, coupling)[encode(spec.target)] == scalar_cost(
        spec, "bank_contiguous"
    )
    if horizon == "long" and coupling == "coupled":
        assert scalar_cost(spec, "bank_contiguous") is None


def test_simultaneous_updates_guard_identity_and_fixed_read_write_counts():
    world = Truth(guards=(0,) * 6, gains=(1,) * 6, spill_gains=(2,) * 6)
    zero = (0,) * 6
    assert step(world, Structure(coupling="independent"), zero, 2) == (0, 2, 1, 0, 0, 0)
    assert step(world, Structure(coupling="coupled"), zero, 2) == (0, 0, 1, 2, 0, 0)
    assert step(world, Structure(), (1, 0, 0, 0, 0, 0), 2) == (1, 0, 0, 0, 0, 0)
    for coupling in ("independent", "coupled"):
        spec = Structure(coupling=coupling)
        for mode in range(6):
            after = step(world, spec, zero, mode)
            assert sum(a != b for a, b in zip(zero, after)) == 2
            for _ in range(4):
                after = step(world, spec, after, mode)
            assert after == zero


def test_blocked_operation_is_charged_probe_is_not_committed_invalid_controls_atomic():
    ep = episode(resource=0)
    spec = ep.public.investigation.data()
    session = Session(ep)
    assert session.act(0, TakeAction(artifact="seal")).ok
    blocked = next(c.machine for i, c in enumerate(spec.topology) if spec.resolved.guards[i] != 0)
    before = session.state.artifacts["seal"].payload.copy()
    result = session.act(1, OperateAction(machine=blocked, artifact="seal"))
    assert (
        result.ok and result.current_turn == 2 and session.state.artifacts["seal"].payload == before
    )
    enabled = next(c.machine for i, c in enumerate(spec.topology) if spec.resolved.guards[i] == 0)
    result = session.act(2, ProbeAction(machine=enabled, artifact="seal"))
    assert result.ok and session.state.artifacts["seal"].payload == before
    assert any(
        event["details"]["result"]["payload"] != before
        for event in result.events
        if "result" in event["details"]
    )
    snapshot = canonical_hash(session.state)
    for action in (
        ConfigureAction(machine=enabled, settings=(0,)),
        OperateAction(machine="reset", artifact="seal"),
    ):
        assert not session.act(3, action).ok
        assert canonical_hash(session.state) == snapshot
    assert not session.act(3, FinishAction()).victory_code
    for action in actions_for(spec, optimal(spec).modes)[1:]:
        result = session.act(session.state.turn, action)
    assert result.victory_code
    assert result.performance.decision_diagnostics.escape_classification == "supported_win"
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)


@pytest.mark.parametrize("resource", [0, 1, 2])
def test_public_policy_finishes_at_exact_cost_and_receipt_needs_finish(resource):
    ep = episode(horizon="long", resource=resource)
    spec = ep.public.investigation.data()
    minimum = optimal(spec).actions
    assert ep.public.initial_state.resources.actions_remaining == (
        None if resource == 0 else minimum + (max(6, (minimum + 1) // 2) if resource == 1 else 0)
    )
    session = Session(ep)

    class PublicPlayer:
        def act(self, **kwargs):
            return session.act(**kwargs)

        def status(self):
            return session.status()

    result = public_policy(PublicPlayer(), ep.public.evidence_files)
    assert result.current_turn == minimum and result.victory_code
    assert qualify_episode(ep).passed
    if resource == 2:
        assert session.state.resources.actions_remaining == 0
    session = Session(ep)
    for action in actions_for(spec, optimal(spec).modes)[:-1]:
        result = session.act(session.state.turn, action)
    assert not result.victory_code
    if resource == 2:
        session.act(session.state.turn, WaitAction())
        assert not session.act(session.state.turn, FinishAction()).victory_code
        assert session.state.terminal_status.value == "failed"


def test_public_state_inference_rejects_false_reading_and_has_no_selection_metadata():
    ep = episode()
    spec = ep.public.investigation.data()
    posterior = Belief(spec)
    mode = next(i for i, g in enumerate(spec.resolved.guards) if g == 0)
    after = step(spec.resolved, spec.options, (0,) * 6, mode)
    posterior.observe(
        Measurement(spec.topology[mode].machine, {"registers": after, "committed": False})
    )
    assert posterior.registers == (0,) * 6
    with pytest.raises(ValueError, match="contradicts"):
        posterior.observe(
            Measurement(spec.topology[mode].machine, {"registers": (0,) * 6, "committed": True})
        )
    public = json.loads(ep.public.model_dump_json())
    text = json.dumps(public)
    for private in (
        "construction_seed",
        "kernel_attempt",
        "horizon_stratum",
        "reference_plan",
        "verifier_secret",
    ):
        assert private not in text
    assert "horizon" not in spec.options.model_dump()


@pytest.mark.parametrize(
    "options",
    [{"horizon": "huge"}, {"coupling": "hidden"}, {"banks": 3}, {"modulus": 7}, {"horizon": True}],
)
def test_unsupported_options_rejected(options):
    with pytest.raises(ValueError):
        GenerationOptions.model_validate(options)


@pytest.mark.parametrize(
    "field",
    [
        "target",
        "truth",
        "topology",
        "seed",
        "evidence",
        "budget",
        "metadata",
        "initial_state",
        "reference",
        "secret",
    ],
)
def test_compiled_contract_tampering_rejected(field):
    data = episode().model_dump(mode="json")
    payload = data["public"]["investigation"]["payload"]
    if field == "target":
        payload["target"][0] = payload["target"][0] % 4 + 1
    elif field == "truth":
        data["investigation_truth"]["payload"]["gains"][0] = (
            data["investigation_truth"]["payload"]["gains"][0] % 4 + 1
        )
    elif field == "topology":
        payload["topology"][0]["spill_register"] = payload["topology"][0]["guard_register"]
    elif field == "seed":
        data["construction_seed"] = 79
    elif field == "evidence":
        data["public"]["evidence_files"]["theory.json"] = "{}"
    elif field == "budget":
        data["public"]["initial_state"]["resources"]["actions_remaining"] += 1
    elif field == "metadata":
        data["generation_metadata"]["investigation_certificate"]["horizon_stratum"] = "long"
    elif field == "initial_state":
        data["public"]["initial_state"]["artifacts"]["seal"]["payload"]["registers"][0] = 1
    elif field == "reference":
        data["reference_plan"] = [{"type": "finish"}]
    else:
        data["verifier_secret"] = ""
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(data)


@pytest.mark.parametrize("values", [(0,) * 5, (0,) * 7, (True, 0, 0, 0, 0, 0), (5, 0, 0, 0, 0, 0)])
def test_register_dimensions_and_values_are_strict(values):
    with pytest.raises(ValueError):
        Specimen(registers=values)


def test_generation_exhaustion_fails_closed_without_substituting_seed(monkeypatch):
    from nexus.ontology.interference import generation

    monkeypatch.setattr(generation, "MAX_KERNEL_ATTEMPTS", 0)
    with pytest.raises(ValueError, match="no substitute seed"):
        generation.selection(987654321)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"theory_level": 1},
        {"discovery_level": 1},
        {"planning_level": 3},
        {"resource_pressure": True},
        {"seed": False},
        {"budget_profile": "diagnostic-plus6"},
    ],
)
def test_unsupported_axes_and_types_rejected(kwargs):
    from nexus.ontology.interference.generation import generate_episode as generate

    with pytest.raises(ValueError):
        generate(**({"seed": 67} | kwargs))
