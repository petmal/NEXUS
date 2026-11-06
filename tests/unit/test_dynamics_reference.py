"""Cold-cache identity, independent proof checking, and behavior compatibility."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from nexus.generator import generate_episode
from nexus.ontology.dynamics import reference_cache as cache
from nexus.ontology.dynamics.policy import public_policy
from nexus.ontology.dynamics.reference_proof import check
from nexus.protocol.session import Session


def test_checked_artifact_and_root_bound():
    nodes = cache.load()
    assert len(nodes) == 3043
    root = nodes[(1 << 1944) - 1]
    assert (root.readings, root.work) == (8, 52)
    check(nodes)
    with pytest.raises(TypeError):
        nodes[1] = root


@pytest.mark.parametrize("corruption", ("truncated", "altered", "self_hash", "stale", "oversized"))
def test_cache_rejects_corrupt_or_stale_data(corruption):
    raw = cache.PATH.read_bytes()
    sources = cache.source_binding()
    digest = cache.SHA256
    if corruption == "truncated":
        raw = raw[:-1]
    elif corruption == "altered":
        raw = raw.replace(b'"version":1', b'"version":2')
    elif corruption == "self_hash":
        raw = raw.replace(b'"version":1', b'"version":2')
        digest = hashlib.sha256(raw).hexdigest()
    elif corruption == "stale":
        sources = {**sources, "ontology/dynamics/laws.py": "changed"}
    else:
        raw = b"x" * (cache.MAX_BYTES + 1)
    with pytest.raises(ValueError):
        cache.decode(raw, digest, sources)


def test_missing_cache_falls_back_without_changing_bound(monkeypatch, tmp_path):
    from nexus.ontology.dynamics.inference import choose, policy_bound

    cache.load.cache_clear()
    monkeypatch.setattr(cache, "PATH", tmp_path / "absent.json")
    choose.cache_clear()
    policy_bound.cache_clear()
    try:
        assert not cache.load()
        assert policy_bound((1 << 1944) - 1) == (8, 52)
    finally:
        cache.load.cache_clear()
        choose.cache_clear()
        policy_bound.cache_clear()


def test_fresh_process_generation_does_not_compile_witness():
    code = """
from nexus.ontology.dynamics import inference
from nexus.ontology.dynamics.generation import generate_dynamics
def forbidden():
    raise AssertionError("cold generation compiled reference")
inference.witness_rows = forbidden
assert generate_dynamics(219).generation_metadata.action_budget == 73
"""
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)


def test_unchanged_dynamics_episode_contracts():
    for row in json.loads(
        (Path(__file__).parents[1] / "fixtures/dynamics-contracts.json").read_text()
    ):
        episode = generate_episode(
            row["seed"],
            axis_version=2,
            science_family="coupled-dynamics-v1",
            planning_level=row["planning"],
            theory_level=row["theory"],
            discovery_level=row["discovery"],
            resource_pressure=1,
            verifier_secret="compatibility-test",
            presentation_version="sealed-facility-v1",  # Historical whole-episode snapshots.
        )
        data = episode.model_dump(mode="json")
        data["public"]["episode_id"] = "nonce"
        assert (
            hashlib.sha256(
                json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            == row["sha256"]
        )


@pytest.mark.slow
def test_reuse_never_exceeds_legacy_actual_work_for_any_world():
    for seed in range(1944):
        episode = generate_episode(
            seed,
            axis_version=2,
            science_family="coupled-dynamics-v1",
            theory_level=3,
            discovery_level=5,
            planning_level=1,
            resource_pressure=1,
        )
        improved, legacy = Session(episode), Session(episode)
        a = public_policy(improved, episode.public.evidence_files)
        b = public_policy(legacy, episode.public.evidence_files, reuse=False)
        assert a.victory_code and b.victory_code and a.current_turn <= b.current_turn, seed


def test_independent_checker_rejects_false_bound_and_false_leaf():
    from dataclasses import replace

    root = (1 << 1944) - 1
    for node in (
        replace(cache.load()[root], work=1),
        replace(cache.load()[root], query=None, readings=0, work=0),
    ):
        nodes = dict(cache.load())
        nodes[root] = node
        with pytest.raises(ValueError):
            check(nodes)
