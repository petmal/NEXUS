from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from nexus.protocol.transport import (
    ClientError,
    check_health,
    request_service_payload,
    validate_candidate_payload,
)


def _write_json(value: object) -> None:
    sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\n")


def _health(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="nexus health",
        description="Exit successfully when a NEXUS service is healthy.",
    )
    parser.add_argument("--url")
    args = parser.parse_args(argv)

    try:
        check_health(url=args.url)
    except ClientError as exc:
        print(f"unhealthy: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write("ok\n")
    return 0


def _request(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="nexus request",
        description="Send one player-safe request to a single-session service.",
    )
    parser.add_argument("--request-file", required=True)
    parser.add_argument("--url")
    args = parser.parse_args(argv)

    try:
        request = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
        response = request_service_payload(request, url=args.url)
    except (json.JSONDecodeError, OSError, ClientError) as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 2

    _write_json(response)
    return 0


def _validate(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="nexus validate",
        description="Validate a submitted victory code against a live single-session service.",
    )
    candidate = parser.add_mutually_exclusive_group(required=True)
    candidate.add_argument("--candidate")
    candidate.add_argument("--candidate-file")
    parser.add_argument("--url")
    args = parser.parse_args(argv)

    try:
        supplied = (
            args.candidate
            if args.candidate is not None
            else Path(args.candidate_file).read_text(encoding="utf-8")
        )
        result = validate_candidate_payload(supplied, url=args.url)
    except (OSError, ClientError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 2

    _write_json(result)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        raise ValueError("fast client command is required")

    command, command_args = args[0], args[1:]
    if command == "health":
        return _health(command_args)
    if command == "request":
        return _request(command_args)
    if command == "validate":
        return _validate(command_args)
    raise ValueError(f"unsupported fast client command: {command}")
