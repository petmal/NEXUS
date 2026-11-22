"""Behavioral regression contracts."""

from itertools import product


def test_every_two_state_binary_machine_pair_matches_bounded_word_oracle():
    from nexus.solver.finite_machine import FiniteMachine

    machines = [FiniteMachine(outputs, transitions)
                for outputs in product(range(2), repeat=2)
                for transitions in product(tuple(product(range(2), repeat=2)), repeat=2)]
    words = [word for length in range(4) for word in product(range(2), repeat=length)]

    def read(machine, word):
        state = 0
        for symbol in word:
            state = machine.transitions[symbol][state]
        return machine.outputs[state]

    signatures = [machine.signature() for machine in machines]
    observations = [[read(machine, word) for word in words] for machine in machines]
    # A shortest distinguishing word cannot revisit a product state. There
    # are four product states, so length <= 3 covers all-history inequivalence.
    for i, left in enumerate(machines):
        for j, right in enumerate(machines):
            differing = next((word for word, a, b in zip(words, observations[i], observations[j])
                              if a != b), None)
            assert left.counterexample(right) == differing
            assert (signatures[i] == signatures[j]) == (differing is None)
