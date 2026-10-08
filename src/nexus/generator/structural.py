"""Complete bounded T3 prior and an exact quotient over unreachable shape contexts."""
from dataclasses import dataclass
from itertools import product
import csv
import io
import json
from math import prod

from nexus.diagnostics import timed_call
from nexus.engine.rules import apply_effect
from nexus.models.episode import PrivateEpisode
from nexus.models.rules import Condition, ConditionKind, Effect, EffectKind
from nexus.models.world import Artifact, Shape

OPERATIONS = ("add1", "add2", "multiply2")
CELLS = tuple(product(Shape, (0, 1)))
FAMILY = "t3-independent-operator-cells-v1"
INVARIANTS = ("shape", "pattern", "orientation", "polarity")


def operation_effect(name: str) -> Effect:
    if name not in OPERATIONS:
        raise ValueError("unsupported structural operator")
    if name == "multiply2":
        return Effect(kind=EffectKind.MULTIPLY_MOD, field="value", multiplier=2, modulus=11)
    return Effect(kind=EffectKind.ADD_MOD, field="value", amount=1 if name == "add1" else 2, modulus=11)


@dataclass(frozen=True)
class StructuralPrior:
    domains: tuple[tuple[str, ...], ...] = (OPERATIONS,) * 6

    def __post_init__(self):
        if len(self.domains) != len(CELLS) or any(
            not domain or len(set(domain)) != len(domain)
            or any(op not in OPERATIONS for op in domain) for domain in self.domains
        ):
            raise ValueError("invalid structural domains")

    @property
    def cardinality(self) -> int:
        return prod(map(len, self.domains))

    def public_json(self) -> str:
        return json.dumps(dict(family=FAMILY, modulus=11, context=["shape", "phase_parity"],
            independent_cells=True, invariant_fields=list(INVARIANTS),
            cells=[dict(shape=s.value, parity=p, operations=list(d))
                   for (s, p), d in zip(CELLS, self.domains, strict=True)]), indent=2, sort_keys=True)

    def manual(self) -> str:
        return (
            "T3 MISSING RELATIONSHIP\n"
            "No effective or baseline machine law is supplied. Construct a predictive law from "
            "measurements within this complete bounded structural prior: each shape/parity cell "
            "independently chooses one fixed operator. add1 means value+1, add2 means value+2, "
            "multiply2 means value*2; all arithmetic is modulo 11. There is no promised formula "
            "or correlation across cells. All invariant_fields are preserved. Laws are deterministic, "
            "stationary and memoryless, with no room, identity, turn, pattern or history dependence. "
            "Measurements are truthful. The actual mission is physically solvable; hypotheses with "
            "no successful trajectory contradict that promise.\n" + self.public_json()
        )

    def law(self, choices: tuple[str, ...]) -> Effect:
        if len(choices) != 6 or any(op not in domain for op, domain in zip(choices, self.domains, strict=True)):
            raise ValueError("structural law outside disclosed domains")
        return Effect(kind=EffectKind.SEQUENCE, effects=tuple(
            Effect(kind=EffectKind.CONDITIONAL,
                condition=Condition(kind=ConditionKind.AND, children=(
                    Condition(kind=ConditionKind.EQUALS, field="shape", value=shape.value),
                    Condition(kind=ConditionKind.PHASE_PARITY, parity="even" if parity == 0 else "odd"),
                )), effects=(operation_effect(op),))
            for (shape, parity), op in zip(CELLS, choices, strict=True)))

    def full_laws(self) -> list[Effect]:
        """Bounded exhaustive oracle for tests/PoCs; runtime uses the proven quotient."""
        return [self.law(choices) for choices in product(*self.domains)]

    def contains(self, law: Effect) -> bool:
        choices = []
        for branch, domain in zip(law.effects, self.domains):
            matching = [op for op in domain if branch.effects == (operation_effect(op),)]
            if len(matching) != 1:
                return False
            choices.append(matching[0])
        return len(choices) == 6 and self.law(tuple(choices)) == law

    def observe(self, item: Artifact, phase: int, output: Artifact) -> "StructuralPrior":
        if any(getattr(item, field) != getattr(output, field) for field in INVARIANTS):
            raise ValueError("structural measurement violates invariant fields")
        index = CELLS.index((item.shape, phase % 2))
        domains = list(self.domains)
        domains[index] = tuple(op for op in domains[index]
                              if apply_effect(operation_effect(op), item, phase).value == output.value)
        if not domains[index]:
            raise ValueError("structural measurement contradicts prior")
        return StructuralPrior(tuple(domains))

    def project(self, episode: PrivateEpisode) -> tuple[list[Effect], int]:
        """All available artifacts retain one shape under every law and ordinary action."""
        shapes = {a.shape for a in episode.public.initial_state.artifacts.values()}
        if len(shapes) != 1 or set(episode.machine_rules) != {"M1"}:
            raise ValueError("T3 projection requires one reachable shape and one machine")
        indices = [i for i, (shape, _) in enumerate(CELLS) if shape in shapes]
        multiplicity = prod(len(d) for i, d in enumerate(self.domains) if i not in indices)
        representatives = []
        for values in product(*(self.domains[i] for i in indices)):
            choices = [d[0] for d in self.domains]
            for index, value in zip(indices, values, strict=True):
                choices[index] = value
            representatives.append(self.law(tuple(choices)))
        if len(representatives) * multiplicity != self.cardinality:
            raise ValueError("incomplete structural projection")
        return representatives, multiplicity


def read_structural_prior(files: dict[str, str]) -> StructuralPrior:
    prior = StructuralPrior()
    if files.get("theory.json") != prior.public_json() or files.get("facility_manual.txt") != prior.manual():
        raise ValueError("invalid complete T3 public prior")
    return prior


@timed_call("structural.evidence_projection")
def structural_belief(episode: PrivateEpisode) -> StructuralPrior:
    prior = read_structural_prior(episode.public.evidence_files)
    try:
        rows = list(csv.DictReader(io.StringIO(episode.public.evidence_files["measurements.csv"])))
        if len(rows) != 1:
            raise ValueError("T3 requires one independent calibration")
        row = rows[0]
        item = Artifact(id="sample", location="lab", shape=row["shape"], pattern="plain",
                        value=int(row["input_value"]), orientation=row["input_orientation"],
                        polarity=row["input_polarity"])
        output = item.model_copy(update={field: int(row[f"output_{field}"]) if field == "value" else row[f"output_{field}"]
                                        for field in ("value", "orientation", "polarity")})
        if int(row["phase"]) != 0 or item.shape == episode.public.initial_state.artifacts["A1"].shape:
            raise ValueError("T3 calibration must use another shape at phase zero")
        belief = prior.observe(item, 0, output)
        if belief.cardinality != 243:
            raise ValueError("T3 calibration must identify exactly one cell")
        return belief
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid T3 calibration: {exc}") from exc
