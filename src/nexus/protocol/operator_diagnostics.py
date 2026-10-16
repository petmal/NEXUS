"""Opt-in private stderr journal and read-only lifecycle reports.

Never mounted as an HTTP endpoint or included in an active player response.
The journal contains committed actions, not live posterior hints. A hard process
kill may prevent a shutdown report; operators can reconstruct from this journal.
"""

import json
import logging
from threading import RLock

LOGGER = logging.getLogger("nexus.operator")


class OperatorDiagnostics:
    def __init__(self, session):
        self.session = session
        self.cursor = 0
        self._lock = RLock()
        self._terminal_reported = False

    def emit(self, kind, payload):
        LOGGER.info(
            "NEXUS operator diagnostic: %s",
            json.dumps(
                {
                    "version": "operator-diagnostic-v1",
                    "kind": kind,
                    "episode_id": self.session.episode.public.episode_id,
                    **payload,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )

    def start(self):
        from nexus.evaluation.matrix import source_digest

        episode = self.session.episode
        metadata = episode.generation_metadata
        self.emit(
            "binding",
            {
                "source_sha256": source_digest(),
                "seed": episode.construction_seed,
                "family": metadata.scenario_family_id,
                "theory": metadata.theory_level,
                "discovery": metadata.discovery_level,
                "planning": metadata.planning_level,
                "resource_pressure": metadata.resource_pressure,
                "budget_profile": metadata.budget_profile,
                "initial_action_budget": metadata.action_budget,
            },
        )

    def checkpoint(self):
        """Drain committed trace once, including concurrent/idempotent requests."""
        with self._lock:
            for record in self.session.trace_snapshot()[self.cursor :]:
                self.emit(
                    "action",
                    {
                        "turn": record.turn,
                        "action": record.action.model_dump(mode="json"),
                        "before_hash": record.before_hash,
                        "after_hash": record.after_hash,
                    },
                )
                self.cursor += 1
            if (
                self.session.state_snapshot().terminal_status.value != "active"
                and not self._terminal_reported
            ):
                self.report("terminal")
                self._terminal_reported = True

    def report(self, trigger):
        try:
            self.emit("report", {"trigger": trigger, **self.session.operator_snapshot()})
        except Exception:
            # Diagnostics must not change action semantics or hide service shutdown.
            LOGGER.exception("NEXUS operator diagnostic report failed")
