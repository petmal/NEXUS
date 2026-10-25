"""Small completely disclosed graphs; P labels describe layouts, not calibrated ranks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Layout:
    rooms: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    mode_rooms: tuple[str, str, str, str]
    name: str
    start: str = "array"
    finish: str = "array"


LAYOUTS = (
    Layout(("array",), (), ("array", "array", "array", "array"), "co-located"),
    Layout(
        ("array", "annex"), (("array", "annex"),), ("array", "annex", "array", "annex"), "split"
    ),
    Layout(
        ("array", "a", "b", "c", "d"),
        tuple(("array", r) for r in ("a", "b", "c", "d")),
        ("a", "b", "c", "d"),
        "hub",
    ),
    Layout(
        ("array", "a", "b", "c", "d", "e"),
        (
            ("array", "a"),
            ("a", "b"),
            ("b", "c"),
            ("c", "d"),
            ("d", "e"),
            ("e", "array"),
            ("b", "e"),
        ),
        ("a", "c", "d", "b"),
        "circuit",
    ),
)


@lru_cache(maxsize=256)
def route(planning: int, start: str, end: str) -> tuple[str, ...]:
    """Shortest route, excluding the starting room; every edge is public."""
    layout = LAYOUTS[planning]
    if start not in layout.rooms or end not in layout.rooms:
        raise ValueError("route endpoint outside disclosed layout")
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(start, ())])
    seen = {start}
    while queue:
        here, path = queue.popleft()
        if here == end:
            return path
        adjacent = sorted(b if a == here else a for a, b in layout.edges if here in (a, b))
        for there in adjacent:
            if there not in seen:
                seen.add(there)
                queue.append((there, (*path, there)))
    raise ValueError("disclosed graph is disconnected")
