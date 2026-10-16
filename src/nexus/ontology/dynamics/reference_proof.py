"""Offline compiler/checker for the original public policy, bypassing its cache."""

import hashlib
import json
from functools import cache

from nexus.ontology.dynamics.inference import experiment_cost, target_set, witness_rows
from nexus.ontology.dynamics.laws import WORLDS, experiments
from nexus.ontology.dynamics.reference_cache import Node, decode, source_binding


def compile_nodes():
    rows, queries = witness_rows(), experiments(2)
    nodes = {}

    @cache
    def visit(mask):
        if len(target_set(mask)) == 1:
            node = Node(None, 0, 0)
        else:
            # Deliberately independent of cached choose()/policy_bound().
            scores = []
            for index, row in enumerate(rows):
                sizes = [(mask & outcome).bit_count() for outcome in row]
                scores.append(
                    (max(sizes), sum(n * n for n in sizes), len(queries[index].history), index)
                )
            selected = min(scores)[3]
            children = [mask & outcome for outcome in rows[selected] if mask & outcome]
            if mask in children:
                raise ValueError("reference cannot resolve target")
            descendants = [visit(child) for child in children]
            node = Node(
                selected,
                1 + max(n.readings for n in descendants),
                experiment_cost(queries[selected]) - 1 + max(n.work for n in descendants),
            )
        nodes[mask] = node
        return node

    visit((1 << len(WORLDS)) - 1)
    return nodes


def check(nodes):
    """Check reachability, strict refinement, terminal validity and recurrence."""
    reached = set()
    rows, queries = witness_rows(), experiments(2)

    def visit(mask):
        if mask in reached:
            return
        reached.add(mask)
        node = nodes[mask]
        if node.query is None:
            if len(target_set(mask)) != 1 or (node.readings, node.work) != (0, 0):
                raise ValueError("invalid reference leaf")
            return
        children = [mask & part for part in rows[node.query] if mask & part]
        if mask in children:
            raise ValueError("reference does not refine belief")
        for child in children:
            visit(child)
        bound = (
            1 + max(nodes[m].readings for m in children),
            experiment_cost(queries[node.query]) - 1 + max(nodes[m].work for m in children),
        )
        if bound != (node.readings, node.work):
            raise ValueError("invalid reference recurrence")

    visit((1 << len(WORLDS)) - 1)
    if reached != set(nodes):
        raise ValueError("unreachable reference nodes")
    if dict(nodes) != compile_nodes():
        raise ValueError("reference differs from original greedy policy")


def serialized():
    nodes = compile_nodes()
    check(nodes)
    raw = (
        json.dumps(
            {
                "version": 1,
                "sources": source_binding(),
                "nodes": [
                    [format(mask, "x"), node.query, node.readings, node.work]
                    for mask, node in sorted(nodes.items())
                ],
            },
            separators=(",", ":"),
        )
        + "\n"
    ).encode()
    decode(raw, hashlib.sha256(raw).hexdigest(), source_binding())
    return raw
