"""Disk-backed trace audit: exact events, JSON types and non-consuming actions."""

from __future__ import annotations

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER
from nexus.models.events import TraceRecord


def test_jsonl_replay_verifies_measurement_events_and_observation_turns():
    e = generate_episode(
        7,
        axis_version=2,
        science_family="resonant-network-v1",
        discovery_level=5,
        theory_level=3,
        planning_level=0,
        resource_pressure=0,
        verifier_secret="replay-audit-test-secret",
    )
    actions = [ACTION_ADAPTER.validate_python({"type": "observe"})]
    actions += [ACTION_ADAPTER.validate_python(action) for action in e.reference_plan]
    state, trace = execute_with_trace(e, actions)
    loaded = [TraceRecord.model_validate_json(record.model_dump_json()) for record in trace]
    assert loaded[0].turn == 0
    assert canonical_hash(replay(e, loaded)) == canonical_hash(state)

    for field, replacement, message in (
        ("turn", 999, "turn mismatch"),
        ("events", (), "events mismatch"),
    ):
        damaged = list(loaded)
        probe_index = next(i for i, rec in enumerate(loaded) if rec.action.type == "probe")
        damaged[probe_index] = loaded[probe_index].model_copy(update={field: replacement})
        with pytest.raises(ValueError, match=message):
            replay(e, damaged)

    # Alter a plausible scientific reading while keeping valid state hashes.
    damaged = [rec.model_copy(deep=True) for rec in loaded]
    reading_event = next(
        event
        for rec in damaged
        for event in rec.events
        if event.details.get("result", {}).get("sample", {}).get("reading") is not None
    )
    sample = reading_event.details["result"]["sample"]
    sample["reading"] = (sample["reading"] + 1) % 7
    with pytest.raises(ValueError, match="events mismatch"):
        replay(e, damaged)

    # JSON scalar types are part of the audit record, even when Python equality
    # considers them equivalent (e.g. 0 == False, or 3 == 3.0).
    for field, convert in (("x", bool), ("reading", float)):
        damaged = [rec.model_copy(deep=True) for rec in loaded]
        event = next(
            event
            for rec in damaged
            if rec.action.type == "probe"
            for event in rec.events
            if "result" in event.details
        )
        sample = event.details["result"]["sample"]
        assert sample[field] == convert(sample[field])
        sample[field] = convert(sample[field])
        with pytest.raises(ValueError, match="events mismatch"):
            replay(e, damaged)
