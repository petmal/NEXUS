"""Opt-in operator timing; never part of the player protocol or compiled episode."""

import logging
import json
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter, process_time

logger = logging.getLogger("nexus.generation")
_stages: ContextVar[dict | None] = ContextVar("generation_stages", default=None)
_path: ContextVar[tuple[str, ...]] = ContextVar("generation_path", default=())


def generation_diagnostics(function):
    """One bounded summary per generation, including failures and repeated nested stages."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        if not logger.isEnabledFor(logging.INFO):
            return function(*args, **kwargs)
        stages = {}
        token = _stages.set(stages)
        path_token = _path.set(())
        started, cpu_started = perf_counter(), process_time()
        outcome = "complete"
        try:
            return function(*args, **kwargs)
        except BaseException:
            outcome = "error"
            raise
        finally:
            summary = {
                "event": outcome, "wall_seconds": perf_counter() - started,
                "cpu_seconds": process_time() - cpu_started,
                "stages": stages,
            }
            _stages.reset(token)
            _path.reset(path_token)
            logger.info("event=generation_summary summary=%s", json.dumps(summary, sort_keys=True),
                        extra={"generation_summary": summary})
    return wrapped


def timed_call(stage: str):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with timed_stage(stage):
                return function(*args, **kwargs)
        return wrapped
    return decorate


@contextmanager
def timed_stage(stage: str):
    metrics: dict[str, int | float] = {}
    if not logger.isEnabledFor(logging.INFO):
        yield metrics
        return
    logger.info("stage=%s event=start", stage)
    path = (*_path.get(), stage)
    token = _path.set(path)
    started, cpu_started = perf_counter(), process_time()
    outcome = "complete"
    try:
        yield metrics
    except BaseException:
        outcome = "error"
        raise
    finally:
        seconds = perf_counter() - started
        cpu_seconds = process_time() - cpu_started
        _path.reset(token)
        stages = _stages.get()
        if stages is not None:
            entry = stages.setdefault("/".join(path), {
                "count": 0, "errors": 0, "wall_seconds": 0.0, "cpu_seconds": 0.0,
            })
            entry["count"] += 1
            entry["errors"] += outcome == "error"
            entry["wall_seconds"] += seconds
            entry["cpu_seconds"] += cpu_seconds
        logger.info(
            "stage=%s event=%s seconds=%.6f cpu_seconds=%.6f metrics=%s",
            stage, outcome, seconds, cpu_seconds, metrics,
            extra={"generation_timing": {
                "stage": stage, "path": "/".join(path), "event": outcome,
                "seconds": seconds, "cpu_seconds": cpu_seconds, **metrics,
            }},
        )
