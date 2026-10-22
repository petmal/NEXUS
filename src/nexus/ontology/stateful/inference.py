"""Public-only posterior over correlated laws and committed physical state."""

from nexus.ontology.stateful.laws import WORLD_INDEX, WORLDS, encode, history_states, readout


class Belief:
    def __init__(self, spec):
        self.spec = spec
        self.worlds = (
            tuple(range(len(WORLDS))) if spec.resolved is None else (WORLD_INDEX[spec.resolved],)
        )
        self.history = ()
        self.target = encode(spec.target)

    def counts(self):
        # Decision universe is {finish now}, not an enumeration of future plans.
        states = history_states(self.history)
        return len(self.worlds), len({states[w] == self.target for w in self.worlds})

    def observe(self, measurement):
        history = tuple(measurement.sample["history"])
        states = history_states(history)
        reading = measurement.sample["reading"]
        self.worlds = tuple(w for w in self.worlds if readout(states[w]) == reading)
        if not self.worlds:
            raise ValueError("stateful observation contradicts the public prior")
        if measurement.sample["committed"]:
            self.history = history

    def accepting_count(self, history):
        if history is None:
            return 0
        states = history_states(tuple(history))
        return sum(states[w] == self.target for w in self.worlds)

    def supports(self, history):
        return (
            bool(self.worlds)
            and history is not None
            and self.accepting_count(history) == len(self.worlds)
        )

    def common_decisions(self):
        return (self.history,) if self.supports(self.history) else ()

    def exclude_target(self, history):
        if history is not None:
            states = history_states(tuple(history))
            self.worlds = tuple(w for w in self.worlds if states[w] != self.target)
            if not self.worlds:
                raise ValueError("rejected finish contradicts the public posterior")
