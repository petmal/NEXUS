"""Singleton public law and current full vector, without private truth access."""

from nexus.ontology.interference.laws import step


class Belief:
    def __init__(self, spec):
        self.spec = spec
        self.registers = (0,) * spec.options.count
        self.worlds = (spec.resolved,)

    def counts(self):
        # The decision universe is immediate finish, whose result is fully known.
        return 1, 1

    def observe(self, measurement):
        mode = next(
            (
                index
                for index, item in enumerate(self.spec.topology)
                if item.machine == measurement.instrument
            ),
            None,
        )
        if mode is None:
            raise ValueError("unknown public coordinate measurement")
        after = tuple(measurement.sample["registers"])
        if after != step(self.spec.resolved, self.spec.options, self.registers, mode):
            raise ValueError("observation contradicts the disclosed law or current vector")
        if measurement.sample["committed"]:
            self.registers = after

    def accepting_count(self, registers):
        return int(registers is not None and tuple(registers) == self.spec.target)

    def supports(self, registers):
        return bool(self.accepting_count(registers))

    def common_decisions(self):
        return (self.registers,) if self.supports(self.registers) else ()

    def exclude_target(self, registers):
        if self.supports(registers):
            raise ValueError("eligible rejected finish contradicts the public target")
