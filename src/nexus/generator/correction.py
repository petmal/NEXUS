"""Complete public effective-theory prior and its finite-domain proof."""
from dataclasses import asdict, dataclass
from itertools import product
import json

from nexus.engine.rules import apply_effect
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Orientation, Pattern, Polarity, Shape


@dataclass(frozen=True)
class CorrectionPrior:
    family: str = "t2-effective-phase-correction-v1"
    effective_add: int = 1
    modulus: int = 11
    validity_phases: tuple[int, ...] = (0, 2)
    correction_phases: tuple[int, ...] = (1, 3)
    correction_add_choices: tuple[int, ...] = (0, 1, 2)
    invariant_fields: tuple[str, ...] = ("shape", "pattern", "orientation", "polarity")

    def public_json(self):
        return json.dumps(asdict(self), sort_keys=True, indent=2)

    def manual(self):
        return (
            "T2 EFFECTIVE THEORY\n"
            "Machines are deterministic, stationary and memoryless. The effective model adds "
            "effective_add to value modulo modulus, preserving all invariant_fields. It is "
            "guaranteed exact in validity_phases only, for every artifact input. Outside that "
            "region, after the effective model, one additive correction applies: each phase "
            "in correction_phases independently selects a fixed amount from "
            "correction_add_choices. The selected amounts are unknown. They have no other "
            "input, location, identity, turn or history dependence. All combinations are allowed. "
            "Established measurements are truthful. The actual mission is physically solvable; "
            "a hypothesis with no successful trajectory is incompatible with this promise. "
            "Extrapolating the effective model outside its validity region is not guaranteed.\n"
            + self.public_json()
        )

    def add(self, amount):
        return Effect(kind=EffectKind.ADD_MOD, field="value", amount=amount, modulus=self.modulus)

    def effective(self):
        return self.add(self.effective_add)

    def hypotheses(self):
        # The very same public lists drive all combinations; no private subset.
        laws = []
        for amounts in product(self.correction_add_choices, repeat=len(self.correction_phases)):
            corrections = tuple(
                Effect(kind=EffectKind.CONDITIONAL,
                       condition=Condition(kind=ConditionKind.PHASE_EQUALS, value=phase),
                       effects=(self.add(amount),))
                for phase, amount in zip(self.correction_phases, amounts, strict=True)
            )
            laws.append(Effect(kind=EffectKind.SEQUENCE, effects=(self.effective(), *corrections)))
        return laws


def prove_domain(spec):
    laws = spec.hypotheses()
    checked = 0
    signatures = [[] for _ in laws]
    for shape, pattern, value, orientation, polarity, phase in product(
        Shape, Pattern, range(spec.modulus), Orientation, Polarity, range(4),
    ):
        item = Artifact(id="sample", location="lab", shape=shape, pattern=pattern,
                        value=value, orientation=orientation, polarity=polarity)
        effective = apply_effect(spec.effective(), item, phase)
        for index, law in enumerate(laws):
            actual = apply_effect(law, item, phase)
            if phase in spec.validity_phases:
                assert actual == effective
            assert all(getattr(actual, name) == getattr(item, name) for name in spec.invariant_fields)
            signatures[index].append(actual.value)
            checked += 1
    assert len({tuple(signature) for signature in signatures}) == len(laws)
    return checked



def read_correction_prior(files: dict[str, str]) -> CorrectionPrior:
    """Accept only the published family; prose and JSON must describe the same prior."""
    try:
        payload = json.loads(files["theory.json"])
        amount = payload["effective_add"]
        if type(amount) is not int or amount not in (1, 2, 3):
            raise ValueError("unsupported effective addition")
        spec = CorrectionPrior(effective_add=amount)
        if files["theory.json"] != spec.public_json() or files["facility_manual.txt"] != spec.manual():
            raise ValueError("public correction prior differs from its complete evaluator family")
        return spec
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid T2 public correction theory") from exc
