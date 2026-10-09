"""Exact finite-field evaluation of composed relationship programs and preparations."""

from __future__ import annotations

from functools import lru_cache

from nexus.models.network import BENCH, FIELD, NetworkExpression, NetworkTruth


def evaluate(expression: NetworkExpression, values: dict[str, int]) -> int:
    if expression.op == "variable":
        return values[expression.variable] % 7
    left, right = (evaluate(child, values) for child in expression.children)
    return (left + right if expression.op == "add" else left * right) % 7


@lru_cache(maxsize=27)
def program(gates: tuple[int, int, int]) -> tuple[NetworkExpression, ...]:
    def var(name):
        return NetworkExpression(op="variable", variable=name)

    def add(a, b):
        return NetworkExpression(op="add", children=(a, b))

    def mul(a, b):
        return NetworkExpression(op="multiply", children=(a, b))

    x, y, a, b, c, d, u, v = map(var, ("x", "y", "a", "b", "c", "d", "u", "v"))
    left = (add(x, a), mul(x, a), add(mul(x, x), a))[gates[0]]
    right = (add(y, b), mul(y, b), add(mul(y, y), b))[gates[1]]
    output = (
        add(add(mul(u, v), mul(c, mul(u, u))), mul(d, mul(v, v))),
        add(mul(add(u, c), mul(v, v)), mul(d, u)),
        add(mul(add(mul(u, u), c), v), mul(d, mul(u, v))),
    )[gates[2]]
    return left, right, output


def response(truth: NetworkTruth, x: int, y: int) -> int:
    values = {"x": x, "y": y, "a": truth.a, "b": truth.b, "c": truth.c, "d": truth.d}
    values["u"] = evaluate(truth.program[0], values)
    values["v"] = evaluate(truth.program[1], values)
    return evaluate(truth.program[2], values)


def measurement(truth: NetworkTruth, name: str) -> int:
    point = tuple(map(int, name.split(":")))
    if point not in BENCH:
        raise ValueError("meter is calibrated only at the listed bench coordinates")
    return response(truth, *point)


def settings(truth: NetworkTruth) -> tuple[int, ...]:
    return (0, *(response(truth, *point) for point in FIELD))


def prepare(point: tuple[int, int], machine: str) -> tuple[int, int]:
    x, y = point
    if machine == "shift":
        return ((x + 1) % 7, y)
    if machine == "shear":
        return (x, (x + y + 1) % 7)
    raise ValueError("unknown preparation apparatus")
