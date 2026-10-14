"""Serialized public witness and a fixed-batch interpreter.

The tree contains every scientific choice before play. Only expected_turn and
an opaque specimen handle are filled during a batch. No intermediate reply
changes a command, skips a command, or chooses a batch length. Terminal halt is
absorbing and automatic. This is a witness, not the upper-bound policy class.
"""

import json
from dataclasses import asdict, dataclass
from functools import lru_cache

from pydantic import TypeAdapter

from nexus.models.actions import ACTION_ADAPTER
from nexus.ontology.repair.laws import solution
from nexus.solver.finite_game import Program


@dataclass(frozen=True, slots=True)
class PublicProgram:
    actions: tuple[str, ...]  # canonical JSON templates; $survey is an opaque handle
    root: Program
    feedback_rounds: int
    action_upper: int


def check_program(program: PublicProgram):
    """Check literal command indices, response branches and declared resource ceilings."""
    for template in program.actions:
        ACTION_ADAPTER.validate_json(template)

    def visit(node):
        if not node.commands or any(
            type(i) is not int or not 0 <= i < len(program.actions) for i in node.commands
        ):
            raise ValueError("invalid fixed command word")
        signatures = [key for key, _ in node.branches]
        if len(set(signatures)) != len(signatures) or any(
            len(key) != len(node.commands) for key in signatures
        ):
            raise ValueError("invalid feedback partition")
        children = [visit(child) for _, child in node.branches]
        return (
            (1 + max(r for r, _ in children)) if children else 0,
            len(node.commands) + (max(n for _, n in children) if children else 0),
        )

    rounds, actions = visit(program.root)
    if rounds != program.feedback_rounds or rounds > 3 or actions != program.action_upper:
        raise ValueError("public policy exceeds or misstates its declared scope")
    return program


def _reading(values):
    return json.dumps(values, separators=(",", ":"))


@lru_cache(maxsize=4)
def witness(planning, failed_attempt=None):
    if planning not in (0, 1):
        raise ValueError("unknown public topology")
    templates = {}

    def command(kind, **fields):
        encoded = json.dumps({"type": kind, **fields}, sort_keys=True, separators=(",", ":"))
        if encoded not in templates:
            templates[encoded] = len(templates)
        return templates[encoded]

    def commit(dose):
        return (
            command("configure", machine="doser", settings=dose),
            command("operate", machine="doser", artifact="seal"),
            command("finish"),
        )

    def prepare(mode, coordinate):
        return (
            command("configure", machine="stage", settings=(mode, coordinate)),
            command("operate", machine="stage", artifact="$survey"),
            command("operate", machine="coupler", artifact="$survey"),
            command("probe", machine="reader", artifact="$survey"),
        )

    setup = (command("take", artifact="seal"), command("take", artifact="stock"))
    if planning:
        setup += (command("move", target="array"),)
    if failed_attempt is not None:
        setup += commit(failed_attempt)
    root_commands = (*setup, command("probe", machine="reference", artifact="$survey"))
    branches = []
    for a in range(7):
        second = []
        for b in range(7):
            third = tuple(
                (
                    ("ok", "ok", "ok", _reading([c, (c + pow(2, degree, 7)) % 7])),
                    Program(commit(solution(a, b, c, degree))),
                )
                for c in range(7)
                for degree in (1, 2, 3)
            )
            second.append((("ok", "ok", "ok", _reading([b])), Program(prepare(1, b), third)))
        branches.append(
            ((*("ok" for _ in setup), _reading([a])), Program(prepare(0, a), tuple(second)))
        )
    program = PublicProgram(
        tuple(templates),
        Program(root_commands, tuple(branches)),
        3,
        14 + planning + (3 if failed_attempt is not None else 0),
    )
    # Execute the serialized representation, not the builder's Python closures.
    decoded = TypeAdapter(PublicProgram).validate_json(json.dumps(asdict(program)), strict=True)
    return check_program(decoded)


def execute(player, program):
    node, handle, rounds = program.root, None, 0
    while True:
        replies = []
        # node.commands is immutable and fixed before dispatching this entire batch.
        for index in node.commands:
            request = json.loads(program.actions[index])
            if request.get("artifact") == "$survey":
                if handle is None:
                    raise ValueError("unbound opaque survey handle")
                request["artifact"] = handle
            action = ACTION_ADAPTER.validate_python(request)
            result = player.act(expected_turn=player.status().turn, action=action)
            if result.victory_code:
                return result
            if not result.ok:
                raise ValueError(f"public policy action failed: {result.message}")
            if request == {"type": "take", "artifact": "stock"}:
                handle = next(
                    e["details"]["artifact"] for e in result.events if e["type"] == "take"
                )
            symbol = "ok"
            if action.type == "probe" and action.machine in ("reference", "reader"):
                reading = next(
                    e["details"]["result"]["payload"]["reading"]
                    for e in result.events
                    if "result" in e["details"]
                )
                symbol = _reading(reading)
            replies.append(symbol)
        if not node.branches:
            raise ValueError("fixed final continuation did not win")
        rounds += 1
        if rounds > program.feedback_rounds:
            raise ValueError("feedback scope exceeded")
        successor = dict(node.branches).get(tuple(replies))
        if successor is None:
            raise ValueError("public witness has no branch for this reply")
        node = successor


def public_policy(player, *, failed_attempt=None):
    manifest = player.manifest()
    records = {name: player.evidence(name) for name in manifest.evidence_files}
    mapping = json.loads(records["map.json"])
    functions = mapping.get("sector_functions", mapping["rooms"])
    lab = next(room for room, role in functions.items() if role == "Sealed array")
    planning = int(player.observe().room != lab)
    return execute(
        player, witness(planning, None if failed_attempt is None else tuple(failed_attempt))
    )
