"""Known-law coordination contracts and independent finite-state proofs."""

import json
from collections import deque
from copy import deepcopy

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import replay
from nexus.generator import generate_episode, qualify_episode
from nexus.models.actions import (
    ConfigureAction,
    DropAction,
    FinishAction,
    MoveAction,
    OperateAction,
    ProbeAction,
    TakeAction,
    WaitAction,
)
from nexus.models.episode import PrivateEpisode
from nexus.ontology.coordination import runtime
from nexus.ontology.coordination.generation import generate_episode as generate_coordination
from nexus.ontology.coordination.generation import selection
from nexus.ontology.coordination.inference import Belief
from nexus.ontology.coordination.laws import step
from nexus.ontology.coordination.layout import layout_for
from nexus.ontology.coordination.planner import actions_for, bank_contiguous_cost, optimal
from nexus.ontology.coordination.policy import public_policy
from nexus.ontology.coordination.proof import (
    independent_bank_minima,
    physical_minimum,
    prove_kernel,
    scalar_step,
)
from nexus.ontology.coordination.schema import (
    FAMILY,
    GenerationOptions,
    Investigation,
    Specimen,
    Truth,
)
from nexus.ontology.inference import Measurement
from nexus.protocol.session import Session
from nexus.solver import solve


def episode(seed=41, *, banks=2, width=2, coupling="coupled", planning=0, resource=2):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=FAMILY,
        theory_level=0,
        discovery_level=0,
        planning_level=planning,
        resource_pressure=resource,
        ontology_options={"banks": banks, "registers_per_bank": width, "coupling": coupling},
        verifier_secret="coordination-test",
    )


def act(session, action):
    return session.act(expected_turn=session.status().turn, action=action)


@pytest.mark.parametrize("seed", [41, 53])
@pytest.mark.parametrize("banks,width", [(2, 2), (2, 3), (3, 2), (3, 3)])
def test_paired_selection_reachable_independent_factorization_and_strict_interleaving(
    seed, banks, width
):
    independent = episode(seed, banks=banks, width=width, coupling="independent")
    coupled = episode(seed, banks=banks, width=width)
    left, right = (item.public.investigation.data() for item in (independent, coupled))
    assert left.target == right.target and all(left.target)
    assert left.resolved == right.resolved == independent.investigation_truth.data()
    assert left.resolved == coupled.investigation_truth.data()
    assert all(item.cross_first is None for item in left.topology)
    assert sum(item.cross_first is not None for item in right.topology) == banks
    assert tuple(item.local_next for item in left.topology) == tuple(
        item.local_next for item in right.topology
    )
    assert optimal(left).actions == sum(independent_bank_minima(left)) + 2
    assert optimal(left).actions == bank_contiguous_cost(left) == physical_minimum(left)
    assert optimal(right).actions == physical_minimum(right) < bank_contiguous_cost(right)
    assert independent.public.initial_state.machines == coupled.public.initial_state.machines
    for ep in (independent, coupled):
        report = qualify_episode(ep)
        assert report.passed, report.errors


@pytest.mark.parametrize("seed", [41, 53])
@pytest.mark.parametrize("coupling", ["independent", "coupled"])
def test_largest_spatial_optimum_matches_unit_edge_bfs_and_live_public_only_policy(seed, coupling):
    ep = episode(seed, banks=3, width=3, coupling=coupling, planning=3)
    spec = ep.public.investigation.data()
    plan = optimal(spec)
    assert plan.actions == physical_minimum(spec) == solve(ep).optimal_action_count
    assert plan.moves > 0 and plan.explored <= 3**9 * 6
    assert len(actions_for(spec, plan.modes)) == plan.actions
    session = Session(ep)

    class PublicPlayer:
        """The policy is deliberately not passed the Session's private attributes."""

        __slots__ = ()

        def act(self, **kwargs):
            return session.act(**kwargs)

        def status(self):
            return session.status()

    result = public_policy(PublicPlayer(), ep.public.evidence_files)
    assert result.victory_code and result.current_turn == plan.actions
    assert session.state.resources.actions_remaining == 0
    diagnostics = result.performance.decision_diagnostics
    assert diagnostics.escape_classification == "supported_win"
    assert diagnostics.final_evidence.remaining_worlds == 1
    assert diagnostics.submissions[0].evidence.classification == "guaranteed"
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)
    assert not act(session, WaitAction()).ok


def restricted_scalar_cost(spec):
    """Independent unit-edge baseline with explicit completed-bank history."""
    layout = layout_for(spec)
    width = spec.options.registers_per_bank
    initial = (0,) * spec.options.count, layout.start, 0, -1
    queue = deque([(*initial, 1)])
    seen = {initial}
    while queue:
        state, room, used, previous, cost = queue.popleft()
        if state == spec.target and room == layout.finish:
            return cost + 1
        children = [
            (state, right if left == room else left, used, previous)
            for left, right in layout.edges
            if room in (left, right)
        ]
        for mode, destination in enumerate(layout.mode_rooms):
            bank = mode // width
            if room != destination:
                continue
            if bank != previous:
                if used & (1 << bank):
                    continue
                if previous >= 0:
                    start = previous * width
                    if state[start : start + width] != spec.target[start : start + width]:
                        continue
            children.append((scalar_step(spec, state, mode), room, used | (1 << bank), bank))
        for child in children:
            if child not in seen:
                seen.add(child)
                queue.append((*child, cost + 1))
    raise ValueError("restricted target unreachable")


@pytest.mark.parametrize("planning", [0, 3])
@pytest.mark.parametrize("coupling", ["independent", "coupled"])
@pytest.mark.parametrize("banks,width", [(2, 2), (2, 3), (3, 2)])
def test_all_orders_bank_baseline_matches_independent_restricted_bfs(
    planning, coupling, banks, width
):
    spec = episode(
        banks=banks, width=width, coupling=coupling, planning=planning
    ).public.investigation.data()
    assert bank_contiguous_cost(spec) == restricted_scalar_cost(spec)


@pytest.mark.parametrize("coupling", ["independent", "coupled"])
def test_complete_largest_admitted_kernel_matches_independent_scalar_physics(coupling):
    spec = episode(banks=3, width=3, coupling=coupling).public.investigation.data()
    assert prove_kernel(spec) == 3**9 * 9


def test_maximum_vector_is_not_a_special_absorbing_collapse_and_operations_preserve_other_banks():
    options = GenerationOptions(coupling="independent")
    truth = Truth(gains=(1, 1, 1, 1), powers=(2, 2, 2, 2))
    vector = (2, 2, 2, 2)
    assert step(truth, options, vector, 0) == (1, 2, 2, 2)
    for mode in range(4):
        after = step(truth, options, vector, mode)
        assert all(value == vector[index] for index, value in enumerate(after) if index != mode)
        assert step(truth, options, step(truth, options, after, mode), mode) == vector
    # Changing any other bank cannot alter the independent local update.
    assert step(truth, options, (0, 1, 0, 0), 0)[:2] == step(truth, options, (0, 1, 2, 1), 0)[:2]


@pytest.mark.parametrize("resource", [0, 1, 2])
def test_budgets_exact_slack_and_uncapped_diagnostic(resource):
    ep = episode(resource=resource)
    minimum = optimal(ep.public.investigation.data()).actions
    expected = (
        None if resource == 0 else minimum + (max(6, (minimum + 1) // 2) if resource == 1 else 0)
    )
    assert ep.public.initial_state.resources.actions_remaining == expected
    assert ep.generation_metadata.guaranteed_policy_action_count == minimum
    assert ep.public.evidence_files == episode(resource=0).public.evidence_files
    assert qualify_episode(ep).passed


def test_one_wasted_action_exhausts_exact_budget_without_receipt():
    ep = episode()
    session = Session(ep)
    assert act(session, WaitAction()).ok
    for action in runtime.physical_plan(ep):
        result = act(session, action)
    assert not result.victory_code and not result.ok
    assert session.status().status.value == "failed"
    assert session.state.resources.actions_remaining == 0


def test_probe_preview_atomic_invalid_actions_failed_finish_recovery_and_receipts():
    ep = episode(resource=0, planning=3)
    spec = ep.public.investigation.data()
    session = Session(ep)
    assert not act(session, FinishAction()).victory_code
    assert act(session, TakeAction(artifact="seal")).ok
    before = canonical_hash(session.state)
    for invalid in (
        ProbeAction(machine="bank0_r0", artifact="seal"),
        OperateAction(machine="reset", artifact="seal"),
        ConfigureAction(machine="bank0_r0", settings=(0,)),
        TakeAction(artifact="seal"),
    ):
        assert not act(session, invalid).ok
        assert canonical_hash(session.state) == before
    assert act(session, MoveAction(target="a")).ok
    payload = deepcopy(session.state.artifacts["seal"].payload)
    result = act(session, ProbeAction(machine="bank0_r0", artifact="seal"))
    assert result.ok and not result.victory_code
    assert session.state.artifacts["seal"].payload == payload
    preview = next(
        event["details"]["result"]["payload"]
        for event in result.events
        if "result" in event["details"]
    )
    assert tuple(preview["registers"]) == step(spec.resolved, spec.options, (0,) * 4, 0)
    assert not act(session, FinishAction()).victory_code
    assert act(session, MoveAction(target="array")).ok
    assert not act(session, FinishAction()).victory_code
    assert session.state.artifacts["seal"].payload == payload
    # The failed finish did not change the vector; resume the exact public word.
    for action in runtime.physical_plan(ep)[1:]:
        result = act(session, action)
    assert result.victory_code
    diagnostic = result.performance.decision_diagnostics
    assert [item.evidence.classification for item in diagnostic.submissions] == [
        "ineligible",
        "ineligible",
        "contradicted",
        "guaranteed",
    ]
    assert diagnostic.escape_classification == "supported_win"
    assert canonical_hash(replay(ep, session.trace)) == canonical_hash(session.state)


def test_target_vector_without_carried_seal_is_ineligible_and_recoverable():
    ep = episode(resource=0)
    session = Session(ep)
    for action in runtime.physical_plan(ep)[:-1]:
        act(session, action)
    assert act(session, DropAction(artifact="seal")).ok
    assert not act(session, FinishAction()).victory_code
    assert act(session, TakeAction(artifact="seal")).ok
    result = act(session, FinishAction())
    assert result.victory_code
    assert (
        result.performance.decision_diagnostics.submissions[0].evidence.classification
        == "ineligible"
    )


@pytest.mark.parametrize("ineligible", ["dropped", "wrong_room", "neither"])
def test_terminal_log_checks_finish_eligibility(caplog, ineligible):
    ep = episode(resource=0, planning=3)
    session = Session(ep)
    for action in runtime.physical_plan(ep)[:-1]:
        assert act(session, action).ok
    if ineligible == "dropped":
        assert act(session, DropAction(artifact="seal")).ok
    elif ineligible == "wrong_room":
        assert act(session, MoveAction(target="a")).ok
    if ineligible != "neither":
        assert not act(session, FinishAction()).victory_code
    with caplog.at_level("INFO", logger="nexus.diagnostics"):
        session.finalize_attempt()
    expected = "True" if ineligible == "neither" else "False"
    assert f"immediate_finish_supported={expected}" in caplog.text


def test_inference_rejects_false_readings_and_probe_does_not_change_current_state():
    spec = episode().public.investigation.data()
    posterior = Belief(spec)
    after = step(spec.resolved, spec.options, posterior.registers, 0)
    posterior.observe(Measurement("bank0_r0", {"registers": after, "committed": False}))
    assert posterior.registers == (0,) * 4 and posterior.counts() == (1, 1)
    with pytest.raises(ValueError, match="contradicts"):
        posterior.observe(Measurement("bank0_r0", {"registers": (0,) * 4, "committed": True}))
    assert posterior.registers == (0,) * 4


@pytest.mark.parametrize("field", ["banks", "registers_per_bank"])
@pytest.mark.parametrize("value", [True, False, 2.0, "2", 1, 4, None])
def test_options_are_strict_bounded_integers(field, value):
    with pytest.raises(ValueError):
        GenerationOptions.model_validate({field: value})


@pytest.mark.parametrize("options", [{"unknown": 1}, {"coupling": "rewired"}, {"coupling": True}])
def test_options_unknown_fields_and_couplings_rejected(options):
    with pytest.raises(ValueError):
        generate_coordination(41, options=options)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"seed": True},
        {"seed": 41.0},
        {"theory_level": False},
        {"theory_level": 3},
        {"discovery_level": False},
        {"discovery_level": 5},
        {"planning_level": True},
        {"planning_level": 1},
        {"planning_level": 2},
        {"resource_pressure": True},
        {"resource_pressure": 3},
        {"budget_profile": "diagnostic-plus6"},
        {"verifier_secret": ""},
    ],
)
def test_unsupported_axes_and_types_rejected(kwargs):
    with pytest.raises(ValueError):
        generate_coordination(**({"seed": 41} | kwargs))


@pytest.mark.parametrize(
    "field",
    [
        "truth",
        "resolved",
        "target",
        "topology",
        "seed",
        "evidence",
        "budget",
        "metadata",
        "registers",
        "location",
        "machines",
        "room",
        "edges",
        "phase",
        "reference",
        "secret",
    ],
)
def test_compiled_episode_tampering_rejected(field):
    data = episode().model_dump(mode="json")
    public = data["public"]
    payload = public["investigation"]["payload"]
    if field in ("truth", "resolved"):
        law = data["investigation_truth"]["payload"] if field == "truth" else payload["resolved"]
        law["gains"][0] = 3 - law["gains"][0]
    elif field == "target":
        payload["target"][0] = 3 - payload["target"][0]
    elif field == "topology":
        payload["topology"][0]["local_next"] = 0
    elif field == "seed":
        data["construction_seed"] = 53
    elif field == "evidence":
        public["evidence_files"]["theory.json"] = "{}"
    elif field == "budget":
        public["initial_state"]["resources"]["actions_remaining"] -= 1
    elif field == "metadata":
        data["generation_metadata"]["recommended_tool_call_limit"] = 1
    elif field == "registers":
        public["initial_state"]["artifacts"]["seal"]["payload"]["registers"][0] = 1
    elif field == "location":
        public["initial_state"]["artifacts"]["seal"]["location"] = "@inventory"
    elif field == "machines":
        public["initial_state"]["machines"]["bank0_r0"]["uses_remaining"] = 1
    elif field == "room":
        public["rooms"]["array"]["label"] = "forged"
    elif field == "edges":
        public["edges"] = [["array", "array"]]
    elif field == "phase":
        public["phase_modulus"] = 2
    elif field == "reference":
        data["reference_plan"] = [{"type": "finish"}]
    else:
        data["verifier_secret"] = ""
    with pytest.raises(ValueError):
        PrivateEpisode.model_validate(data)


def test_dimension_and_cell_type_tampering_rejected_and_public_has_no_solution():
    ep = episode()
    spec = ep.public.investigation.data()
    for field, value in (("target", (1, 1)), ("target", (True, 1, 1, 1)), ("theory", False)):
        with pytest.raises(ValueError):
            Investigation.model_validate(spec.model_dump() | {field: value})
    for vector in ((0, 0), (True, 0, 0, 0), (3, 0, 0, 0), (0,) * 10):
        with pytest.raises(ValueError):
            Specimen(registers=vector)
    public = ep.public.model_dump_json()
    for private in (
        "construction_seed",
        "verifier_secret",
        "reference_plan",
        "procedure",
        "investigation_truth",
    ):
        # Narrative explicitly says no supplied procedure; only check JSON fields.
        assert f'\\"{private}\\":' not in public and f'"{private}":' not in public
    theory = json.loads(ep.public.evidence_files["theory.json"])
    assert theory["specification"] == spec.model_dump(mode="json")
    assert selection(41, 2, 2) == (spec.resolved, spec.target)
    with pytest.raises(ValueError):
        selection(True, 2, 2)
