"""Opt-in operator timing; never part of the player protocol or compiled episode."""

import logging
from contextlib import contextmanager
from time import perf_counter

logger = logging.getLogger("nexus.generation")


@contextmanager
def timed_stage(stage: str):
    metrics: dict[str, int | float] = {}
    if not logger.isEnabledFor(logging.INFO):
        yield metrics
        return
    logger.info("stage=%s event=start", stage)
    started = perf_counter()
    outcome = "complete"
    try:
        yield metrics
    except BaseException:
        outcome = "error"
        raise
    finally:
        seconds = perf_counter() - started
        logger.info(
            "stage=%s event=%s seconds=%.6f metrics=%s",
            stage, outcome, seconds, metrics,
            extra={"generation_timing": {
                "stage": stage, "event": outcome, "seconds": seconds, **metrics,
            }},
        )
