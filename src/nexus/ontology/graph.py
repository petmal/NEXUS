"""Immutable, validated dependency graphs over trusted exact primitives.

This validates composition, not epistemic difficulty. Each family must separately
prove identifiability and the value of dependencies under its public experiments.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    name: str
    primitive: str
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class InvestigationGraph:
    inputs: tuple[str, ...]
    nodes: tuple[Node, ...]
    outputs: tuple[str, ...]

    def __post_init__(self):
        known = set(self.inputs)
        if len(known) != len(self.inputs):
            raise ValueError("duplicate graph input")
        for node in self.nodes:
            if node.name in known or not set(node.inputs) <= known:
                raise ValueError("graph must be acyclic, ordered and have unique names")
            known.add(node.name)
        if not self.outputs or not set(self.outputs) <= known:
            raise ValueError("graph output is undefined")

    def evaluate(self, inputs: Mapping[str, object], primitives: Mapping[str, Callable]) -> tuple:
        if set(inputs) != set(self.inputs):
            raise ValueError("graph input contract mismatch")
        if any(node.primitive not in primitives for node in self.nodes):
            raise ValueError("unknown graph primitive")
        values = dict(inputs)
        for node in self.nodes:
            values[node.name] = primitives[node.primitive](*(values[k] for k in node.inputs))
        return tuple(values[key] for key in self.outputs)


# Public dependency description: calibration controls access to a second law,
# while both laws contribute to the mission. This alone makes no cost claim.
RESONANT_DEPENDENCIES = InvestigationGraph(
    ("coordinate", "h_law", "g_law", "tuning"),
    (
        Node("h", "evaluate_h", ("h_law", "coordinate")),
        Node("g", "calibrated_g", ("g_law", "coordinate", "h", "tuning")),
        Node("target", "combine", ("h", "g")),
    ),
    ("target",),
)
