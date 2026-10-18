"""Reproduce public greedy witnesses offline; --write updates the packaged asset."""

import argparse
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from time import perf_counter
from typing import TypedDict

from nexus.ontology.transfer.laws import targets
from nexus.ontology.transfer.reference import semantic_digest
from nexus.ontology.transfer.tables import assemble_tables


class Policy(TypedDict):
    readings: int
    nodes: list[list[int | None]]


class Reference(TypedDict):
    version: str
    semantic_digest: str
    targets: tuple[int, ...]
    calibrated: Policy
    coupled: Policy


def tree(coupled: bool, allowed_queries: Iterable[int] | None = None) -> Policy:
    table = assemble_tables(coupled, targets())
    candidates = (
        tuple(range(len(table.outcomes))) if allowed_queries is None else tuple(allowed_queries)
    )
    nodes: list[list[int | None]] = []
    started = perf_counter()

    def visit(mask: int) -> tuple[int, int]:
        if len(nodes) > 16384 or perf_counter() - started > 120:
            raise TimeoutError("offline policy exceeded reviewed node/time cap")
        if table.common(mask):
            physical_index = ((mask & -mask).bit_length() - 1) % 5184
            return -targets()[physical_index] - 1, 0
        index = len(nodes)
        nodes.append([])
        query = min(
            candidates,
            key=lambda i: (
                max((mask & p).bit_count() for p in table.outcomes[i]),
                sum((mask & p).bit_count() ** 2 for p in table.outcomes[i]),
                i,
            ),
        )
        parts = tuple(mask & p for p in table.outcomes[query])
        if mask in parts:
            raise ValueError("unidentifiable mission in complete observation domain")
        children = [visit(p) if p else (None, 0) for p in parts]
        nodes[index] = [query, *(child[0] for child in children)]
        return index, 1 + max(child[1] for child in children)

    _, bound = visit(table.full)
    return {"readings": bound, "nodes": nodes}


def compile_reference() -> Reference:
    return {
        "version": "transfer-reference-v1",
        "semantic_digest": semantic_digest(),
        "targets": targets(),
        "calibrated": tree(False),
        "coupled": tree(True),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    start = perf_counter()
    path = Path(__file__).resolve().parents[1] / "src/nexus/ontology/transfer/reference.json"
    data = compile_reference()
    rendered = json.dumps(data, separators=(",", ":")) + "\n"
    identity = (
        '# Offline public policy identity; update through the compiler.\nSHA256 = "'
        + hashlib.sha256(rendered.encode()).hexdigest()
        + '"\n'
    )
    identity_path = path.with_name("reference_identity.py")
    if args.write:
        path.write_text(rendered)
        identity_path.write_text(identity)
    elif path.read_text() != rendered or identity_path.read_text() != identity:
        raise SystemExit("transfer reference differs; use --write after reviewing semantics")
    print(
        json.dumps(
            {
                "seconds": perf_counter() - start,
                "bytes": len(rendered),
                "calibrated_readings": data["calibrated"]["readings"],
                "coupled_readings": data["coupled"]["readings"],
            }
        )
    )
