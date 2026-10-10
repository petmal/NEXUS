"""Integer law execution. Player operations never evaluate arbitrary source code."""

from __future__ import annotations

from nexus.models.investigation import InvestigationSpec, InvestigationTruth, ScalarExpression
from nexus.models.network import NetworkSpec, NetworkTruth


def evaluate_scalar(expression: ScalarExpression, variables: dict[str, int], modulus=17) -> int:
    if expression.op == "constant":
        return int(expression.value) % modulus
    if expression.op == "variable":
        return variables[str(expression.value)] % modulus
    left, right = (evaluate_scalar(child, variables, modulus) for child in expression.children)
    if expression.op == "add":
        return (left + right) % modulus
    if expression.op == "multiply":
        return left * right % modulus
    if expression.op == "power":
        return pow(left, right, modulus)
    raise ValueError("unknown scalar operator")


def response(truth: InvestigationTruth, source: str, q: int) -> int:
    a = 0 if source == "reference" else truth.properties[int(source)]
    return evaluate_scalar(truth.response, {"a": a, "q": q, "c": truth.coefficient})


def measurement(spec: InvestigationSpec, truth: InvestigationTruth, name: str) -> int:
    if name == "selector":
        return truth.selector
    source, context = name.split(":")
    if context == "property":
        if not spec.material_meter or source == "reference":
            raise ValueError("material measurement is unavailable")
        return truth.properties[int(source)]
    q = int(context)
    if q not in (0, 1, 2) or source not in ("reference", "0", "1"):
        raise ValueError("outside the bench measurement range")
    return (response(truth, source, q) + spec.scale * truth.offset) % spec.modulus


def settings(
    spec: InvestigationSpec | NetworkSpec, truth: InvestigationTruth | NetworkTruth
) -> tuple[int, ...]:
    if isinstance(spec, NetworkSpec):
        if not isinstance(truth, NetworkTruth):
            raise TypeError("network settings require network truth")
        if spec.version == "resonant-network-v1":
            from nexus.engine.resonance import settings as resonant_settings
            return resonant_settings(truth)
        from nexus.engine.network import settings as network_settings
        return network_settings(truth)
    if not isinstance(truth, InvestigationTruth):
        raise TypeError("shared-response settings require shared-response truth")
    sources = (0, 1) if spec.both_stocks else (truth.selector,)
    return (
        truth.selector,
        *(response(truth, str(source), q) for source in sources for q in spec.target_q),
    )
