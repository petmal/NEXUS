"""Use the existing public P0/P3 maps, assigning coordinates round-robin."""

from dataclasses import dataclass

from nexus.ontology.planning.layout import LAYOUTS, route


@dataclass(frozen=True)
class Layout:
    rooms: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    mode_rooms: tuple[str, ...]
    name: str
    start: str = "array"
    finish: str = "array"


def layout_for(spec) -> Layout:
    base = LAYOUTS[spec.planning]
    return Layout(
        base.rooms,
        base.edges,
        tuple(base.mode_rooms[index % len(base.mode_rooms)] for index in range(spec.options.count)),
        base.name,
    )


__all__ = ["layout_for", "route"]
