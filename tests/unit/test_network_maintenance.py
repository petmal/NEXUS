"""Cross-version behavior, fresh-state ownership and saved-trace audit integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from nexus.generator import generate_episode
from nexus.generator.resonance import tables
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.episode import PlayerManifest
from nexus.protocol.session import Session

FIXTURE = json.loads(
    (Path(__file__).parents[1] / "fixtures/network-compatibility-v1.json").read_text()
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def episode(family="resonant-network-v1", *, d=5, t=3, p=0, r=0, seed=7):
    return generate_episode(
        seed,
        axis_version=2,
        science_family=family,
        discovery_level=d,
        theory_level=t,
        planning_level=p,
        resource_pressure=r,
        verifier_secret=FIXTURE["secret"],
    )


@pytest.mark.parametrize("expected", FIXTURE["cases"], ids=lambda row: str(row["case"]))
def test_published_worlds_and_traces_remain_compatible(expected):
    family, seed, d, t, p, r = expected["case"]
    e = episode(family, seed=seed, d=d, t=t, p=p, r=r)
    assert digest(e.model_dump(mode="json")) == expected["episode"]
    assert (
        digest(PlayerManifest.from_episode(e.public).model_dump(mode="json"))
        == expected["manifest"]
    )
    session = Session(e)
    for action in e.reference_plan:
        result = session.act(session.state.turn, ACTION_ADAPTER.validate_python(action))
        assert result.ok
    assert session.state.terminal_status == "won"
    assert digest([rec.model_dump(mode="json") for rec in session.trace]) == expected["trace"]
    assert digest(result.performance.model_dump(mode="json")) == expected["performance"]


@pytest.mark.parametrize("family", ["coupled-network-v1", "resonant-network-v1"])
def test_cached_generation_never_shares_mutable_world_or_metadata(family):
    first = episode(family)
    second = episode(family)
    expected = second.model_dump_json()
    first.public.initial_state.machines["meter"].uses_remaining = 0
    first.public.initial_state.stocks["S0-0"].remaining = 0
    first.generation_metadata.investigation_certificate["family"] = "changed"
    first.public.evidence_files.clear()
    first.reference_plan[0]["type"] = "changed"
    assert second.model_dump_json() == expected
    assert episode(family).model_dump_json() == expected


def test_shared_factor_tables_are_read_only():
    h_rows, g_rows, _, _ = tables()
    for rows in (h_rows, g_rows):
        with pytest.raises(TypeError):
            rows[(0, 0)] = ()
