"""Disk-backed trace audit: exact events, JSON types and non-consuming actions."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json

import pytest

from nexus.engine.canonical import canonical_hash
from nexus.engine.engine import step
from nexus.engine.replay import execute_with_trace, replay
from nexus.generator import generate_episode
from nexus.models.actions import ACTION_ADAPTER, FinishAction, ObserveAction, WaitAction
from nexus.models.events import TraceRecord
from nexus.models.goals import GoalPredicate
from nexus.models.world import TerminalStatus
from nexus.protocol.transport import _validation_result
from nexus.verification.receipt import victory_receipt


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


def test_receipt_matches_independent_standard_hmac_and_binds_every_identity_field():
    episode = generate_episode(17, planning_level=0, verifier_secret="audit-secret-λ")
    episode.public.episode_id = "audit-世界"
    payload = {"protocol_version": episode.public.protocol_version,
               "episode_id": episode.public.episode_id,
               "goal": episode.public.goal.model_dump(mode="json"), "status": "VICTORY"}
    wire = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    digest = hmac.digest("audit-secret-λ".encode(), wire, hashlib.sha256)[:10]
    token = base64.b32encode(digest).decode()
    expected = "NX-" + "-".join(token[i:i + 4] for i in range(0, 16, 4))
    assert victory_receipt(episode) == expected
    assert victory_receipt(type(episode).model_validate_json(episode.model_dump_json())) == expected
    for field in ("secret", "episode", "protocol", "goal"):
        changed = episode.model_copy(deep=True)
        if field == "secret":
            changed.verifier_secret += "changed"
        elif field == "episode":
            changed.public.episode_id += "changed"
        elif field == "protocol":
            changed.public.protocol_version += "changed"
        else:
            changed.public.goal = GoalPredicate(kind="phase_equals", value=0)
        assert victory_receipt(changed) != expected
        assert not _validation_result(expected, "won", victory_receipt(changed))["correct"]


def test_only_successful_finish_issues_receipt_even_at_exact_budget_boundary():
    episode = generate_episode(17, planning_level=0, verifier_secret="terminal-audit")
    plan = [ACTION_ADAPTER.validate_python(a) for a in episode.reference_plan]
    episode.public.initial_state.resources.actions_remaining = len(plan)
    final, trace = execute_with_trace(episode, plan)
    assert final.terminal_status == TerminalStatus.WON
    assert final.resources.actions_remaining == 0
    assert all(record.victory_code is None for record in trace[:-1])
    receipt = trace[-1].victory_code
    assert receipt == victory_receipt(episode)
    assert _validation_result(receipt, "won", receipt)["correct"]
    for status in ("active", "failed"):
        assert not _validation_result(receipt, status, receipt)["correct"]
    for action in (FinishAction(), WaitAction(), ObserveAction()):
        result = step(final, action, episode)
        assert not result.ok and not result.victory_code
        assert canonical_hash(result.state) == canonical_hash(final)
    damaged = [*trace[:-1], trace[-1].model_copy(update={"victory_code": "NX-FORGED"})]
    with pytest.raises(ValueError, match="victory-code"):
        replay(episode, damaged)
    episode.public.initial_state.resources.actions_remaining = len(plan) - 1
    failed, prefix = execute_with_trace(episode, plan[:-1])
    assert failed.terminal_status == TerminalStatus.FAILED
    assert all(record.victory_code is None for record in prefix)
    assert not step(failed, plan[-1], episode).victory_code
