"""Finite public T1 prior, compact behavioral signatures and exact evidence filtering."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import product
import json
import csv
import io
from collections.abc import Iterator

from nexus.engine.rules import apply_effect, evaluate_condition
from nexus.generator.evidence import (
    EvidencePlanningError, Experiment, MissionEvidencePlan, experiment_pool, is_direct_context,
)
from nexus.generator.rules import CONDITION_FORMS, PARITIES, compose_condition
from nexus.models.rules import Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class TheoryPrior:
    level: int = 1
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

    @lru_cache(maxsize=1024)
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

    @lru_cache(maxsize=1024)
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

    def matching_indices(self, csv_text: str) -> tuple[int, ...]:
        remaining = self.all
        for row in csv.DictReader(io.StringIO(csv_text)):
            before = Artifact(
                id="sample", location="lab", shape=Shape(row["shape"]), pattern=Pattern.PLAIN,
                value=int(row["input_value"]), polarity=Polarity(row["input_polarity"]),
                orientation=Orientation(row["input_orientation"]),
            )
            after = before.model_copy(update={
                "value": int(row["output_value"]),
                "polarity": Polarity(row["output_polarity"]),
                "orientation": Orientation(row["output_orientation"]),
            })
            remaining &= self.mask(self.predictions(before, int(row["phase"])), encode(after))
        return tuple(self.indices(remaining))

    def candidates(self, csv_text: str, *, ceiling: int = 32) -> list[Effect]:
        indices = self.matching_indices(csv_text)
        if not indices or len(indices) > ceiling:
            raise EvidencePlanningError(
                f"T1 evidence leaves {len(indices)} candidates; expected 1..{ceiling}; "
                "the public belief must not be truncated"
            )
        return [self.materialize(index) for index in indices]

    def contains(self, rule: Effect, indices: tuple[int, ...]) -> bool:
        if rule.kind != EffectKind.CONDITIONAL or rule.condition not in self.conditions:
            return False

        def flatten(effects):
            for effect in effects:
                if effect.kind == EffectKind.SEQUENCE:
                    yield from flatten(effect.effects)
                else:
                    yield effect

        for branch in (rule.effects, rule.else_effects):
            counts = {"value": 0, "polarity": 0, "orientation": 0}
            for effect in flatten(branch):
                if (effect.kind == EffectKind.ADD_MOD and effect.amount in (1, 2, 3)
                        and effect.modulus == self.spec.modulus):
                    counts["value"] += 1
                elif (effect.kind == EffectKind.MULTIPLY_MOD and effect.multiplier in (2, 3)
                        and effect.modulus == self.spec.modulus):
                    counts["value"] += 1
                elif effect.kind == EffectKind.TOGGLE:
                    counts["polarity"] += 1
                elif effect.kind == EffectKind.ROTATE and effect.amount in range(4):
                    counts["orientation"] += 1
                else:
                    return False
            if any(count > 1 for count in counts.values()):
                return False
        # Compare complete branch behavior, not AST syntax (representatives may differ).
        remaining = sum(1 << index for index in indices)
        for shape, phase, value in product(tuple(Shape), (0, 1), range(11)):
            item = artifact(shape, value)
            remaining &= self.mask(self.predictions(item, phase), encode(apply_effect(rule, item, phase)))
        if not remaining:
            return False
        representative = self.materialize(next(self.indices(remaining)))
        return all(
            apply_effect(rule, item, phase) == apply_effect(representative, item, phase)
            for shape, phase, value, orientation, polarity in product(
                tuple(Shape), (0, 1), range(11), range(4), range(2)
            )
            for item in (artifact(shape, value, orientation, polarity),)
        )

    def evidence_options(
        self, rule: Effect, mission: Artifact, phase: int, level: int,
        *, ceiling: int = 32, max_rows: int = 8, beam_width: int = 24,
        preserve: tuple[Effect, ...] = (),
        established: tuple[Experiment, ...] = (),
    ) -> Iterator[MissionEvidencePlan]:
        """Bounded deterministic beam search; failure does not prove evidence impossibility.

        Keep alternate residual beliefs so a greedy set with multiple predictions but a
        zero-probe viable policy cannot incorrectly stand in for D2. The caller proves D.
        """
        pool = (*experiment_pool(), Experiment(phase=phase, artifact=mission))
        mission_row = self.predictions(mission, phase)
        outcome_masks = tuple(self.mask(mission_row, value) for value in sorted(set(mission_row)))

        def prediction_count(bits: int) -> int:
            return sum(bool(bits & mask) for mask in outcome_masks)

        # Equivalent evidence rows produce the same residual belief. Retain one witness.
        rows: dict[tuple[int, bool], Experiment] = {}
        for experiment in pool:
            direct = is_direct_context(experiment, mission, phase)
            if level and direct:
                continue
            expected = apply_effect(rule, experiment.artifact, experiment.phase)
            if any(apply_effect(candidate, experiment.artifact, experiment.phase) != expected
                   for candidate in preserve):
                continue
            row = self.predictions(experiment.artifact, experiment.phase)
            output = encode(expected)
            rows.setdefault((self.mask(row, output), direct), experiment)
        initial = self.all
        for experiment in established:
            if level and is_direct_context(experiment, mission, phase):
                raise EvidencePlanningError("established evidence must not reveal the mission context")
            expected = apply_effect(rule, experiment.artifact, experiment.phase)
            if any(apply_effect(candidate, experiment.artifact, experiment.phase) != expected
                   for candidate in preserve):
                raise EvidencePlanningError("established evidence removes a preserved hypothesis")
            initial &= self.mask(self.predictions(experiment.artifact, experiment.phase), encode(expected))
        beam = [(initial, established)]
        seen = {initial}
        for _ in range(max_rows):
            next_states = {}
            for remaining, chosen in beam:
                for (mask, direct), experiment in rows.items():
                    if level == 0 and not chosen and not direct:
                        continue
                    filtered = remaining & mask
                    if not filtered or filtered == remaining or filtered in seen:
                        continue
                    count = filtered.bit_count()
                    predictions = prediction_count(filtered)
                    if level == 2 and predictions < 2:
                        continue
                    seen.add(filtered)
                    experiments = (*chosen, experiment)
                    accepted = count <= ceiling and (
                        (level == 0 and count == 1)
                        or (level == 1 and predictions == 1)
                        or (level == 2 and predictions > 1)
                    )
                    if accepted:
                        yield MissionEvidencePlan(
                            experiments=experiments, candidate_count=count,
                            prediction_count=predictions, direct_target_example=level == 0,
                        )
                    score = (predictions, count) if level == 1 else (count, predictions)
                    next_states[filtered] = (score, experiments)
            beam = [(bits, entry[1]) for bits, entry in sorted(
                next_states.items(), key=lambda item: (item[1][0], item[0])
            )[:beam_width]]
            if not beam:
                return


@lru_cache(maxsize=1)
def theory_universe() -> Universe:
    return Universe()


def validate_theory_profile(theory_level: int, discovery_level: int) -> None:
    if theory_level not in (0, 1):
        raise ValueError("theory_level must be 0 (catalogue) or 1 (structural theory)")
    if theory_level == 1 and discovery_level not in (0, 1, 2, 3, 4):
        raise ValueError("T1 currently supports D0-D4; D5 requires a separate theory proof")


def validate_public_theory(files: dict[str, str]) -> None:
    if files.get("theory.json") != SPEC.public_json() or files.get("facility_manual.txt") != SPEC.manual():
        raise ValueError("T1 public theory does not match the evaluator's structural prior")
