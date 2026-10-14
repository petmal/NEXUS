"""Pure-state gates before declaring or registering a live deep profile."""

from itertools import product

from nexus.ontology.repair.laws import relation, residuals, response, solution, transform, worlds
from nexus.ontology.repair.schema import Specimen, Truth


def test_all_worlds_have_public_three_round_solution_with_nonlinear_transfer():
    targets = {}
    for world in worlds():
        raw = Specimen()
        a = transform(world, raw, "reference").reading[0]
        oriented = transform(world, raw, "stage", (0, a))
        assert transform(world, oriented, "reader").reading is None
        b = transform(world, transform(world, oriented, "coupler"), "reader").reading[0]
        oriented = transform(world, raw, "stage", (1, b))
        c, second = transform(world, transform(world, oriented, "coupler"), "reader").reading
        degree = {2: 1, 4: 2, 1: 3}[(second - c) % 7]
        doses = solution(a, b, c, degree)
        assert residuals(world, doses) == (0, 0, 0, 0)
        key = a, b, c, degree
        assert targets.setdefault(doses, key) == key  # Mission targets are bijective.
    assert len(targets) == 7**3 * 3


def test_complete_scalar_response_grammar_and_material_insensitivity():
    # Exhaustive primitive conformance, including off-context measurements.
    for world in worlds():
        for plane, x in product((0, 1), range(7)):
            measured = response(world, (plane, x))
            expected = (
                ((world.b + world.r * (world.a - x)) % 7,)
                if plane == 0
                else tuple(
                    (world.c + z**world.degree + world.r * (world.b - x)) % 7 for z in (0, 2)
                )
            )
            assert measured == expected
        for z in (3, 4):
            assert relation(world, z) == (world.c + z**world.degree) % 7
    # Independent of every hidden variable, including hidden degree.
    key = Specimen(material="seal")
    assert all(transform(w, key, "reader").reading is None for w in worlds())
    assert all(transform(w, Specimen(), "reader").reading is None for w in worlds())


def test_coupling_and_transfer_are_mission_relevant():
    world = Truth(a=2, b=3, c=4, degree=2, r=3)
    assert residuals(world, (world.a, world.b, relation(world, 3), relation(world, 4))) != (
        0,
        0,
        0,
        0,
    )
    assert len({solution(2, 3, 4, d) for d in (1, 2, 3)}) == 3
    # Removing the shared coupling makes the same three fixed contexts sufficient
    # in one feedback batch, with all preparation costs held unchanged.
    for w in worlds():
        uncoupled = w.model_copy(update={"r": 0})
        assert response(uncoupled, (0, 0)) == (w.b,)
        assert response(uncoupled, (1, 0)) == (w.c, (w.c + 2**w.degree) % 7)


def test_reorientation_erases_charge_and_partial_repair_is_reversible():
    world = worlds()[42]
    charged = Specimen(context=(0, 3), charged=True)
    changed = transform(world, charged, "stage", (1, 4))
    assert not changed.charged and changed.context == (1, 4)
    key = transform(world, Specimen(material="seal"), "doser", (6, 6, 6, 6))
    repaired = transform(world, key, "doser", solution(world.a, world.b, world.c, world.degree))
    assert residuals(world, repaired.doses) == (0, 0, 0, 0)


def test_constant_space_seed_decoder_matches_the_exact_uniform_index_order():
    from nexus.ontology.repair.laws import world_at

    assert tuple(world_at(i) for i in range(7203)) == worlds()
    assert world_at(7203) == world_at(0) == world_at(-7203)
