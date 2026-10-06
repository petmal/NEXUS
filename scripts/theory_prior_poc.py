"""Bounded T1 research prior. Not a production generator or supported service option."""

from dataclasses import asdict, dataclass
from functools import cache
from itertools import product
import json

from nexus.engine.rules import apply_effect, evaluate_condition
from nexus.generator.evidence import Experiment, experiment_pool, is_direct_context
from nexus.generator.rules import CONDITION_FORMS, PARITIES, compose_condition
from nexus.models.rules import Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class TheoryPrior:
    condition_forms: tuple[str, ...] = CONDITION_FORMS
    shapes: tuple[str, ...] = tuple(item.value for item in Shape)
    parities: tuple[str, ...] = PARITIES
    value_operations: tuple[str, ...] = ("identity", "add1", "add2", "add3", "multiply2", "multiply3")
    polarity_toggles: tuple[bool, ...] = (False, True)
    rotations: tuple[int, ...] = (0, 1, 2, 3)
    modulus: int = 11

    def public_json(self):
        return json.dumps(asdict(self), sort_keys=True, indent=2)

    def manual(self):
        return (
            "T1 STRUCTURAL THEORY\nMachines are deterministic, stationary and memoryless.\n"
            "Each law is exactly one conditional with independently selected true and false branches.\n"
            "Condition names mean: shape_and_phase = (shape=S AND parity=P); "
            "shape_or_phase = (shape=S OR parity=P); not_shape_and_phase = (shape!=S AND parity=P).\n"
            "Each branch chooses exactly one value operation, one polarity toggle choice, and one "
            "clockwise quarter-turn rotation. Value arithmetic is modulo the declared modulus.\n"
            "Orientation cycles north/east/south/west. Shape and pattern are preserved.\n"
            "No dependence on room, turn, identity, pattern, location or history is permitted.\n"
            "Prior measurements are truthful. Each measurements file identifies its machine.\n"
            "The mission is physically solvable under the actual hidden laws. Hypotheses that "
            "admit no successful trajectory are therefore incompatible with this promise.\n"
            "The complete allowed primitive choices and structural forms are:\n" + self.public_json()
        )


SPEC = TheoryPrior()
ORIENTATIONS = tuple(Orientation)
POLARITIES = tuple(Polarity)


def artifact(shape, value=0, orientation=0, polarity=0):
    return Artifact(id="sample", location="lab", shape=shape, pattern=Pattern.PLAIN,
                    value=value, orientation=ORIENTATIONS[orientation], polarity=POLARITIES[polarity])


def encode(item):
    return item.value * 8 + ORIENTATIONS.index(item.orientation) * 2 + POLARITIES.index(item.polarity)


class Universe:
    """A law is six branch IDs; IDs are unique complete branch behaviors, not AST hashes."""

    def __init__(self, spec=SPEC):
        self.spec = spec
        self.branches = tuple(product(spec.value_operations, spec.polarity_toggles, spec.rotations))
        self.conditions = tuple(compose_condition(form, shape=Shape(shape), parity=parity)
                                for form, shape, parity in product(spec.condition_forms, spec.shapes, spec.parities))
        self.cells = tuple(product(tuple(Shape), (0, 1)))
        by_behavior = {}
        self.raw_count = 0
        for condition_id, condition in enumerate(self.conditions):
            mask = tuple(evaluate_condition(condition, artifact(shape), phase) for shape, phase in self.cells)
            for left, right in product(range(len(self.branches)), repeat=2):
                behavior = bytes(left if value else right for value in mask)
                by_behavior.setdefault(behavior, (condition_id, left, right))
                self.raw_count += 1
        self.behaviors = tuple(by_behavior)
        self.representatives = tuple(by_behavior.values())
        self.columns = tuple(bytes(row[cell] for row in self.behaviors) for cell in range(6))
        self.all = (1 << len(self.behaviors)) - 1

    def branch_ast(self, branch_id):
        operation, toggle, rotation = self.branches[branch_id]
        effects = []
        if operation.startswith("add"):
            effects.append(Effect(kind=EffectKind.ADD_MOD, field="value", amount=int(operation[3:]), modulus=self.spec.modulus))
        elif operation.startswith("multiply"):
            effects.append(Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=int(operation[8:]), modulus=self.spec.modulus))
        if toggle:
            effects.append(Effect(kind=EffectKind.TOGGLE, field="polarity"))
        effects.append(Effect(kind=EffectKind.ROTATE, amount=rotation))
        return tuple(effects)

    def materialize(self, index):
        condition, left, right = self.representatives[index]
        return Effect(kind=EffectKind.CONDITIONAL, condition=self.conditions[condition],
                      effects=self.branch_ast(left), else_effects=self.branch_ast(right))

    @cache
    def row(self, shape, phase, value, orientation, polarity):
        cell = self.cells.index((shape, phase % 2))
        table = bytearray(256)
        for index, (operation, toggle, rotation) in enumerate(self.branches):
            output = value
            if operation.startswith("add"):
                output = (value + int(operation[3:])) % self.spec.modulus
            elif operation.startswith("multiply"):
                output = value * int(operation[8:]) % self.spec.modulus
            table[index] = output * 8 + ((orientation + rotation) % 4) * 2 + (polarity ^ toggle)
        return self.columns[cell].translate(bytes(table))

    def predictions(self, item, phase):
        return self.row(item.shape, phase % 2, item.value, ORIENTATIONS.index(item.orientation), POLARITIES.index(item.polarity))

    @cache
    def mask(self, row, output):
        packed = bytearray((len(row) + 7) // 8)
        for index, value in enumerate(row):
            if value == output:
                packed[index // 8] |= 1 << (index % 8)
        return int.from_bytes(packed, "little")

    @staticmethod
    def indices(bits):
        while bits:
            bit = bits & -bits
            yield bit.bit_length() - 1
            bits ^= bit

    def choose_evidence(self, rule, mission, phase, level, ceiling=32, max_rows=8):
        """Greedy feasibility search; rejection is not a proof that no evidence exists."""
        pool = list(experiment_pool())
        # D0 needs a direct row even if the mission's value is absent from the legacy pool.
        pool.append(Experiment(phase=phase, artifact=mission))
        mission_row = self.predictions(mission, phase)
        outcome_masks = tuple(self.mask(mission_row, value) for value in sorted(set(mission_row)))
        predictions = lambda bits: sum(bool(bits & mask) for mask in outcome_masks)
        rows = []
        for experiment in pool:
            direct = is_direct_context(experiment, mission, phase)
            if level and direct:
                continue
            row = self.predictions(experiment.artifact, experiment.phase)
            output = encode(apply_effect(rule, experiment.artifact, experiment.phase))
            rows.append((experiment, self.mask(row, output), direct))
        remaining = self.all
        chosen = []
        for _ in range(max_rows):
            count, prediction_count = remaining.bit_count(), predictions(remaining)
            if chosen and ((level == 0 and count == 1) or
                           (level == 1 and prediction_count == 1 and count <= ceiling) or
                           (level == 2 and prediction_count > 1 and count <= ceiling)):
                break
            eligible = []
            for index, (_, mask, direct) in enumerate(rows):
                if index in chosen or (level == 0 and not chosen and not direct):
                    continue
                filtered = remaining & mask
                size = filtered.bit_count()
                if size == 0 or size >= count:
                    continue
                n_predictions = predictions(filtered)
                if level == 2 and n_predictions < 2:
                    continue
                score = (n_predictions, size, index) if level == 1 else (size, index)
                eligible.append((score, index, filtered))
            if not eligible:
                break
            _, index, remaining = min(eligible)
            chosen.append(index)
        count, prediction_count = remaining.bit_count(), predictions(remaining)
        accepted = bool(chosen) and count <= ceiling and (
            (level == 0 and count == 1) or (level == 1 and prediction_count == 1) or
            (level == 2 and prediction_count >= 2))
        return {
            "accepted": accepted, "candidate_count": count, "predictions": prediction_count,
            "experiments": tuple(rows[index][0] for index in chosen),
            "indices": tuple(self.indices(remaining)),
        }
