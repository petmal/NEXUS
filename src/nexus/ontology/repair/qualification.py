"""Named fixed-cell qualification; arbitrary budget/prior overrides invalidate it."""

import hashlib
import json
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from pydantic import TypeAdapter

from nexus.ontology.repair.proof import QueryUpperProof, check


@lru_cache(maxsize=1)
def proof_payload():
    return TypeAdapter(QueryUpperProof).validate_json(
        Path(__file__).with_name("query-upper-proof.json").read_text(), strict=True
    )


def check_offline_proof():
    proof = proof_payload()
    check(proof)
    if proof.budget != 15 or proof.upper_mass * 2 > proof.worlds:
        raise ValueError("repair family misses the release success ceiling")
    return proof


def source_binding():
    """Identity of the complete installed Python implementation, not proof by hash."""
    root = Path(__file__).resolve().parents[2]
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.py"))
    }


def witness_binding():
    from nexus.ontology.repair.policy import witness

    return {
        str(p): hashlib.sha256(
            json.dumps(asdict(witness(p)), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        for p in (0, 1)
    }


@lru_cache(maxsize=1)
def release_matches():
    """Installed package is immutable for this process; source changes require restart.

    The checked-in manifest is produced only after proof, conformance, witness and
    review gates. It avoids repeating the offline search during each generation.
    """
    path = Path(__file__).with_name("qualified-release.json")
    try:
        release = json.loads(path.read_text())
        return (
            release["version"] == "repair-live-conformance-v1"
            and release["sources"] == source_binding()
            and release["witnesses"] == witness_binding()
            and release["proof_sha256"]
            == hashlib.sha256(
                Path(__file__).with_name("query-upper-proof.json").read_bytes()
            ).hexdigest()
        )
    except OSError, ValueError, KeyError, TypeError:
        return False


def require_release():
    if not release_matches():
        raise ValueError(
            "repair qualification is missing or stale; rerun the offline release gates"
        )


def certificate(planning):
    proof = proof_payload()
    qualified = release_matches()
    digest = hashlib.sha256(
        Path(__file__).with_name("query-upper-proof.json").read_bytes()
    ).hexdigest()
    return {
        "family": "coupled-repair-v1",
        "status": "qualified" if qualified else "experimental",
        "calibrated": False,
        "profile": "stationary-three-round-v1",
        "truth_count": 7203,
        "prior": "uniform-truth-index",
        "sampler": "seed-modulo7203-v1",
        "seed_mapping": "seed modulo7203; sample uniformly from0..7202 for the stated prior",
        "feedback_round_upper": 3,
        "reference_action_upper": 14 + planning,
        "two_round_success_upper_numerator": proof.upper_mass,
        "two_round_success_upper_denominator": proof.worlds,
        "query_proof_sha256": digest,
        "semantic_release_sha256": hashlib.sha256(
            Path(__file__).with_name("qualified-release.json").read_bytes()
        ).hexdigest()
        if qualified
        else None,
        "live_interface_qualification": "factored-conformance-v1" if qualified else "pending",
        "actual_action_budget": 17 + planning,
        "recovery_allowance": 3,
        "one_extra_action_two_round_success": "1",
        "scope": "one non-resettable attempt; uniform truth indices 0..7202 conditional on each operator-fixed public configuration; independent public nonce; serial application requests; exact P0/P1 R1; no private-process access, timing-side-channel or model-failure claim",
    }


def qualify_repair(episode):
    from nexus.generator.qualify import QualificationReport
    from nexus.models.episode import PrivateEpisode
    from nexus.ontology.repair.policy import public_policy
    from nexus.protocol.session import Session

    try:
        validated = PrivateEpisode.model_validate_json(episode.model_dump_json())
        proof = check_offline_proof()
        p = validated.generation_metadata.planning_level
        result = public_policy(Session(validated))
        checks = {
            "compiled_contract": True,
            "reviewed_source_binding": release_matches(),
            "serialized_witness_binding": release_matches()
            and json.loads(Path(__file__).with_name("qualified-release.json").read_text())[
                "witnesses"
            ]
            == witness_binding(),
            "complete_query_upper_proof": proof.upper_mass * 2 <= proof.worlds,
            "public_three_round_policy_wins": result.victory_code is not None,
            "nominal_budget": result.current_turn == 14 + p,
            "metadata_scope": validated.generation_metadata.investigation_certificate
            == certificate(p),
        }
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        return QualificationReport(
            passed=False, checks={"qualified_contract": False}, errors=(str(exc),), metrics={}
        )
    return QualificationReport(
        passed=all(checks.values()),
        checks=checks,
        errors=tuple(k for k, v in checks.items() if not v),
        metrics={"query_upper": "3/7", "live_status": certificate(p)["status"]},
    )
