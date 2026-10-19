"""Mission uncertainty is joint winning-set intersection, not parameter entropy."""

import pytest

from nexus.evaluation.goal_information import (
    assess_panel,
    feedback_success_ceiling,
    minimum_identifying_panel,
    minimum_supporting_certificate,
)


def test_partial_understanding_can_guarantee_a_common_repair():
    result = assess_panel((0b011, 0b110), ((0,), (0,)), (0,))
    assert result.supported_worlds == 2 and result.unresolved_buckets == 0


def test_pairwise_compatible_worlds_can_have_no_joint_repair():
    # Every pair shares a decision, but the three-way intersection is empty.
    result = assess_panel((0b011, 0b110, 0b101), ((0,),) * 3, (0,))
    assert result.supported_worlds == 0 and result.unresolved_buckets == 1


def test_exact_certificate_handles_overlap_and_higher_order_obstruction():
    assert minimum_supporting_certificate(0b111, (0b011, 0b101), (0b111,)) == ()
    assert minimum_supporting_certificate(0b111, (0b011, 0b101), (0b001,)) == (0, 1)
    assert minimum_supporting_certificate(0b111, (0b011, 0b101), (0b011, 0b101)) == (0,)
    with pytest.raises(ValueError, match="cap reached"):
        minimum_supporting_certificate(0b111, (0b011, 0b101), (0b001,), max_states=1)


def test_feedback_bound_includes_the_required_successful_finish():
    assert [feedback_success_ceiling(216, 3, 1, k) for k in range(8)] == [
        0,
        1,
        3,
        9,
        27,
        81,
        216,
        216,
    ]
    assert feedback_success_ceiling(1024, 9, 96, 1) == 96
    assert feedback_success_ceiling(216, 1, 1, 5) == 5  # finish-only search
    with pytest.raises(ValueError):
        feedback_success_ceiling(0, 3, 1, 1)


def test_teaching_example_rejects_shallow_depth_claim():
    rows = tuple(tuple(pow((u + k) % 3, e, 3) for u in range(3)) for k in range(3) for e in (1, 2))
    assert len(minimum_identifying_panel(rows).queries) == 3
    # Only the first two seals: two possible theories share a correct repair.
    labels = {values: i for i, values in enumerate(sorted({r[:2] for r in rows}))}
    winning = tuple(1 << labels[r[:2]] for r in rows)
    assert assess_panel(winning, rows, (0, 1)).supported_worlds == 6
    with pytest.raises(ValueError, match="does not identify"):
        minimum_identifying_panel(tuple(r[:2] for r in rows))


def test_history_seed_239_common_procedure_is_not_a_guess():
    from nexus.ontology.history.inference import indices, partitions
    from nexus.ontology.history.laws import decisions, word_index, words

    mask = partitions((), 1)[5] & partitions((), 2)[8]
    assert mask.bit_count() == 32
    word = (2, 2, 3, 2, 2)
    assert decisions().accepting[word_index(word)] & mask == mask
    assert words()[word_index(word)] == word
    result = assess_panel(tuple(decisions().winning[i] for i in indices(mask)), ((0,),) * 32, ())
    assert result.supported_worlds == 32
