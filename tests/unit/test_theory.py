"""Exhaustive compositional proof of the finite public T1 contract."""

from itertools import product
from nexus.generator.theory import SPEC, Universe, artifact, encode
from nexus.engine.rules import apply_effect, evaluate_condition
from nexus.generator.evidence import is_direct_context
from nexus.generator.rules import transformation_rule_catalog
from nexus.models.rules import Effect, EffectKind
from nexus.models.world import Shape


def test_t1_full_grammar_counts_and_compositional_engine_equivalence():
    universe = Universe()
    assert universe.raw_count == 41472
    assert len(universe.behaviors) == 27120
    # All 48 branch behaviors on all 88 varying inputs; every condition on all six cells.
    signatures = []
    for branch_id in range(48):
        rule = Effect(kind=EffectKind.SEQUENCE, effects=universe.branch_ast(branch_id))
        signatures.append(bytes(encode(apply_effect(rule, artifact(Shape.TRIANGLE, v, o, p), 0))
                                for v, o, p in product(range(11), range(4), range(2))))
    assert len(set(signatures)) == 48
    for index, behavior in enumerate(universe.behaviors):
        condition_id, left, right = universe.representatives[index]
        condition = universe.conditions[condition_id]
        expected = bytes(left if evaluate_condition(condition, artifact(shape), phase) else right
                         for shape, phase in universe.cells)
        assert behavior == expected
    for shape, phase, v, o, p in product(tuple(Shape), range(2), range(11), range(4), range(2)):
        row = universe.row(shape, phase, v, o, p)
        cell = universe.cells.index((shape, phase))
        offset = v * 8 + o * 2 + p
        assert row == bytes(signatures[behavior[cell]][offset] for behavior in universe.behaviors)


def test_all_t0_rules_are_t1_members_and_filtering_preserves_the_truth():
    universe = Universe()
    for rule in transformation_rule_catalog():
        remaining = universe.all
        for shape, phase, v in product(tuple(Shape), range(2), range(11)):
            item = artifact(shape, v)
            row = universe.predictions(item, phase)
            remaining &= universe.mask(row, encode(apply_effect(rule, item, phase)))
        assert remaining.bit_count() == 1
        representative = universe.materialize(next(universe.indices(remaining)))
        # Joint AST check across the complete 528-context domain for each T0 member.
        for shape, phase, v, o, p in product(tuple(Shape), range(2), range(11), range(4), range(2)):
            item = artifact(shape, v, o, p)
            assert apply_effect(rule, item, phase) == apply_effect(representative, item, phase)


def test_public_prior_and_evidence_are_honest():
    universe = Universe()
    rule = transformation_rule_catalog()[0]
    mission = artifact(Shape.TRIANGLE, 4)
    for level in range(3):
        plan = next(universe.evidence_options(rule, mission, 0, level), None)
        if plan is None:
            continue
        if level:
            assert all(not is_direct_context(e, mission, 0) for e in plan.experiments)
        else:
            assert any(is_direct_context(e, mission, 0) for e in plan.experiments)
        from nexus.generator.evidence import evidence_csv
        candidates = universe.candidates(evidence_csv(rule, plan.experiments))
        for candidate in candidates:
            for e in plan.experiments:
                assert apply_effect(candidate, e.artifact, e.phase) == apply_effect(rule, e.artifact, e.phase)
    assert SPEC.public_json() in SPEC.manual()
    assert "add2_toggle_rotate1" not in SPEC.manual()


def test_t1_policy_matches_ordinary_action_exhaustion():
    from nexus.engine.engine import step
    from nexus.models.actions import FinishAction, OperateAction, ProbeAction, WaitAction
    from nexus.models.world import TerminalStatus
    from nexus.solver.belief import _episode_for_hypothesis, solve_guaranteed_policy
    from nexus.solver.search import search_state_key
    from test_belief_policy import _episode

    universe = Universe()
    # Two honest T1 hypotheses differ in which parity permits the mission transformation.
    left = universe.branches.index(("add1", False, 0))
    right = universe.branches.index(("add2", False, 0))
    rules = [Effect(kind=EffectKind.CONDITIONAL, condition=universe.conditions[index],
                    effects=universe.branch_ast(left), else_effects=universe.branch_ast(right))
             for index in (0, 1)]
    item = artifact(Shape.TRIANGLE).model_copy(update={"id": "A1", "location": "@inventory"})
    episode = _episode(artifacts={"A1": item}, phase_modulus=2)
    worlds = [_episode_for_hypothesis(episode, {"M1": rule}, search_budget=32) for rule in rules]
    actions = (FinishAction(), WaitAction(), OperateAction(machine="M1", artifact="A1"),
               ProbeAction(machine="M1", artifact="A1"))

    def wins(nodes, budget):
        if all(state.terminal_status == TerminalStatus.WON for _, state in nodes):
            return True
        if budget == 0 or any(state.terminal_status != TerminalStatus.ACTIVE for _, state in nodes):
            return False
        for action in actions:
            groups = {}
            for index, state in nodes:
                result = step(state, action, worlds[index])
                if not result.ok:
                    break
                probe = tuple(str(event.details) for event in result.events if event.type == "probe")
                groups.setdefault((search_state_key(result.state), probe), []).append((index, result.state))
            else:
                if all(wins(group, budget - 1) for group in groups.values()):
                    return True
        return False

    nodes = [(index, world.public.initial_state) for index, world in enumerate(worlds)]
    expected = next(budget for budget in range(1, 7) if wins(nodes, budget))
    actual = solve_guaranteed_policy(episode, candidate_rules_by_machine={"M1": rules}, max_actions=6)
    assert actual.optimal_worst_case_actions == expected
