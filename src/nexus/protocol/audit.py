"""Private, source-bound research bundles for one session.

The destination contains the compiled world and its verifier secret. It must not
be mounted into the player sandbox. Exchange/trace journals survive ordinary
process interruption; only a closed manifest claims a finished export.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import tempfile
from pathlib import Path
from threading import Lock

from nexus.engine.canonical import canonical_bytes, canonical_hash
from nexus.engine.replay import replay
from nexus.io import load_private, load_trace
from nexus.models.world import TerminalStatus
from nexus.presentation import evidence_files
from nexus.provenance import source_digest
from nexus.protocol.public_transcript import PublicTranscript

VERSION = "nexus-audit-bundle-v1"
FILES = ("private.json", "binding.json", "exchanges.jsonl", "trace.jsonl", "outcome.json")
REQUEST_COUNTERS = ("invalid_actions", "duplicate_requests", "protocol_conflicts")


def _verify_game_outcome(episode, records, outcome):
    """Recompute game-derived diagnostics; free requests require a separate audit.

    Accepted actions cannot establish invalid/retry/conflict or construction-check
    counts. Preserve that boundary even when a transcript claims full coverage.
    """
    from nexus.protocol.session import Session

    reconstructed = Session(episode)
    for record in records:
        if not reconstructed.act(reconstructed.state.turn, record.action).ok:
            raise ValueError("audit session reconstruction mismatch")
    if outcome["evaluator_finalized"]:
        reconstructed.finalize_attempt()
    expected = reconstructed.operator_snapshot()
    for field in ("status", "performance", "evidence_witnesses", "physical_continuation"):
        if field not in outcome:
            raise ValueError(f"audit {field} mismatch: missing field")
        actual, wanted = outcome[field], expected[field]
        if field == "performance" and isinstance(actual, dict) and isinstance(wanted, dict):
            actual, wanted = dict(actual), dict(wanted)
            for name in REQUEST_COUNTERS:
                value = actual.pop(name, None)
                if type(value) is not int or value < 0:
                    raise ValueError(f"audit performance mismatch: invalid {name}")
                wanted.pop(name)
        if canonical_bytes(actual) != canonical_bytes(wanted):
            raise ValueError(f"audit {field} mismatch")
    return expected


def _atomic_json(path: Path, value: object) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class AuditRecorder:
    """Single writer for a new operator-owned directory; never overwrites a run."""

    def __init__(self, session, directory: Path, transcript: PublicTranscript | None = None):
        self.session = session
        self.directory = Path(directory)
        self.transcript = transcript if transcript is not None else session.public_transcript
        if self.transcript.sink is not None:
            raise ValueError("this transcript already has an audit recorder")
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        self._lock = Lock()
        self._cursor = 0
        self._closed = False
        self._write_error = False
        episode = session.episode
        binding = {
            "version": VERSION,
            "episode_id": episode.public.episode_id,
            "runtime_source_sha256": source_digest(),
            "python_version": platform.python_version(),
            "protocol_version": episode.public.protocol_version,
            "presentation_version": episode.public.presentation_version,
            "generation_metadata": episode.generation_metadata.model_dump(mode="json"),
            "public_evidence_sha256": canonical_hash(evidence_files(episode.public)),
            "initial_state_sha256": canonical_hash(episode.public.initial_state),
            "provider_identity": None,
            "scope": "One local NEXUS session; provider identity, inference settings and billing belong to the external harness.",
        }
        _atomic_json(self.directory / "private.json", episode.model_dump(mode="json"))
        _atomic_json(self.directory / "binding.json", binding)
        for name in ("exchanges.jsonl", "trace.jsonl"):
            with (self.directory / name).open("x", encoding="utf-8"):
                pass
            (self.directory / name).chmod(0o600)
        _atomic_json(self.directory / "manifest.json", {"version": VERSION, "closed": False})
        # Preserve exchanges made before attaching an optional recorder.
        for record in self.transcript.snapshot()["records"]:
            self._append_exchange(json.dumps(record, separators=(",", ":")))
        self.transcript.sink = self._append_exchange
        self.checkpoint()

    def _append_exchange(self, encoded: str) -> None:
        with self._lock:
            if self._closed:
                raise OSError("audit recorder is closed")
            try:
                with (self.directory / "exchanges.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(encoded + "\n")
            except OSError:
                self._write_error = True
                raise

    def checkpoint(self) -> None:
        # Take the session lock before the writer lock, as direct capture does.
        records = self.session.trace_snapshot()
        with self._lock:
            if self._closed:
                return
            try:
                with (self.directory / "trace.jsonl").open("a", encoding="utf-8") as handle:
                    for record in records[self._cursor :]:
                        handle.write(record.model_dump_json() + "\n")
                        self._cursor += 1
            except OSError:
                self._write_error = True
                raise

    def close(self) -> None:
        if self._closed:
            return
        self.checkpoint()
        state, trace, outcome = self.session.audit_snapshot()
        transcript = self.transcript.snapshot()
        outcome.update(
            canonical_state_sha256=canonical_hash(state),
            trace_state_sha256=canonical_hash(replay(self.session.episode, list(trace))),
        )
        _atomic_json(self.directory / "outcome.json", outcome)
        with self._lock:
            manifest = {
                "version": VERSION,
                "closed": True,
                "complete": transcript["complete"] and not self._write_error,
                "exchange_count": len(transcript["records"]),
                "exchanges_seen": transcript["exchanges_seen"],
                "accepted_actions": len(trace),
                "transcript_version": transcript["version"],
                "files_sha256": {
                    name: hashlib.sha256((self.directory / name).read_bytes()).hexdigest()
                    for name in FILES
                },
                "scope": "Private operator bundle. Checksums detect changed bytes, not external authenticity. A missing closed manifest denotes an interrupted export.",
            }
            _atomic_json(self.directory / "manifest.json", manifest)
            self._closed = True
        self.transcript.sink = None

    def checkpoint_safely(self) -> None:
        """Keep recording failures out of the player action response."""
        try:
            self.checkpoint()
        except OSError:
            logging.getLogger("nexus.operator").exception("audit trace write failed")


def verify_bundle(directory: Path) -> dict:
    """Verify source binding, integrity, exact trace, lifecycle and game metrics.

    This does not independently replay every public transport response or verify
    the external harness's model settings. Those are separate research checks.
    """
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != VERSION or manifest.get("closed") is not True:
        raise ValueError("audit bundle is unsupported or not closed; retain it as partial evidence")
    if set(manifest.get("files_sha256", {})) != set(FILES):
        raise ValueError("audit bundle has an invalid file inventory")
    for name in FILES:
        path = directory / name
        if (
            path.is_symlink()
            or hashlib.sha256(path.read_bytes()).hexdigest() != manifest["files_sha256"][name]
        ):
            raise ValueError(f"audit file checksum mismatch: {name}")
    binding = json.loads((directory / "binding.json").read_text(encoding="utf-8"))
    if binding["runtime_source_sha256"] != source_digest():
        raise ValueError("audit runtime source differs; use the recorded NEXUS revision")
    episode = load_private(directory / "private.json")
    if binding["episode_id"] != episode.public.episode_id:
        raise ValueError("audit episode binding mismatch")
    if binding["initial_state_sha256"] != canonical_hash(episode.public.initial_state) or binding[
        "public_evidence_sha256"
    ] != canonical_hash(evidence_files(episode.public)):
        raise ValueError("audit world binding mismatch")
    records = load_trace(directory / "trace.jsonl")
    state = replay(episode, records)
    outcome = json.loads((directory / "outcome.json").read_text(encoding="utf-8"))
    if type(outcome.get("evaluator_finalized")) is not bool:
        raise ValueError("audit evaluator_finalized must be boolean")
    if canonical_hash(state) != outcome["trace_state_sha256"]:
        raise ValueError("audit trace state mismatch")
    if outcome["evaluator_finalized"] and state.terminal_status == TerminalStatus.ACTIVE:
        state.terminal_status = TerminalStatus.FAILED
    if canonical_hash(state) != outcome["canonical_state_sha256"]:
        raise ValueError("audit lifecycle state mismatch")
    verified_outcome = _verify_game_outcome(episode, records, outcome)
    exchanges = [
        json.loads(line)
        for line in (directory / "exchanges.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    if len(records) != manifest["accepted_actions"] or len(exchanges) != manifest["exchange_count"]:
        raise ValueError("audit record count mismatch")
    sequences = [r["sequence"] for r in exchanges]
    if sequences != sorted(set(sequences)) or any(type(n) is not int or n < 1 for n in sequences):
        raise ValueError("audit exchange sequence mismatch")
    if manifest["complete"] and (sequences != list(range(1, manifest["exchanges_seen"] + 1))):
        raise ValueError("audit complete flag contradicts exchange coverage")
    return {
        "version": VERSION,
        "episode_id": episode.public.episode_id,
        "trace_replay_verified": True,
        "receipt_verification": "original_secret_verified"
        if any(r.victory_code for r in records)
        else "no_receipt_in_trace",
        "public_capture_complete": manifest["complete"],
        "public_responses_semantically_verified": False,
        "game_metrics_verified": True,
        "world_qualification_rechecked": False,
        "unverified_outcome_fields": [
            *(f"performance.{name}" for name in REQUEST_COUNTERS),
            "assistance", "provider_stop_reason", "receipt_validation",
        ],
        "accepted_actions": len(records),
        "exchange_count": len(exchanges),
        "world_status": state.terminal_status.value,
        "physical_continuation": verified_outcome["physical_continuation"],
    }
