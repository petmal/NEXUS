"""Bounded operator-side record of actual player-visible exchanges.

This complements, and never changes, the accepted-action replay trace. The
capture boundary is application data, not network timing or proxy behavior.
Overflow marks coverage incomplete instead of silently claiming a full history.
"""

from __future__ import annotations

import base64
import json
import logging
from contextvars import ContextVar
from pathlib import Path
from threading import Lock

VERSION = "public-interactions-v1"
# A transport boundary owns the response projection; Session supplies only effects.
BOUNDARY: ContextVar[list[dict] | None] = ContextVar("nexus_public_boundary", default=None)


class PublicTranscript:
    def __init__(self, *, max_records: int = 10_000, max_bytes: int = 16 * 1024 * 1024):
        if max_records < 1 or max_bytes < 1:
            raise ValueError("transcript limits must be positive")
        self.max_records = max_records
        self.max_bytes = max_bytes
        self._records: list[str] = []
        self._bytes = 0
        self._seen = 0
        self._incomplete = False
        self._lock = Lock()
        self.sink = None

    def append(self, request, response, *, effects=(), transport="direct", complete=True):
        with self._lock:
            self._seen += 1
            if not complete:
                self._incomplete = True
            encoded = json.dumps(
                {
                    "sequence": self._seen,
                    "transport": transport,
                    "request": request,
                    "response": response,
                    "effects": effects,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            size = len(encoded.encode())
            if len(self._records) >= self.max_records or self._bytes + size > self.max_bytes:
                self._incomplete = True
                return
            self._records.append(encoded)
            self._bytes += size
            if self.sink is not None:
                try:
                    self.sink(encoded)
                except OSError:
                    self._incomplete = True
                    # A recording failure must not turn a committed action into
                    # an ambiguous player error. Coverage fails closed instead.
                    logging.getLogger("nexus.operator").exception("audit exchange write failed")

    def snapshot(self):
        with self._lock:
            return {
                "version": VERSION,
                "complete": not self._incomplete,
                "exchanges_seen": self._seen,
                "bytes_retained": self._bytes,
                "records": [json.loads(row) for row in self._records],
            }

    def save(self, path: Path):
        # Operator-owned destination; never exposed through the player API.
        path.write_text(json.dumps(self.snapshot(), indent=2) + "\n", encoding="utf-8")


def record(transcript, request, response, before, after):
    effect = {"before": before, "after": after}
    outer = BOUNDARY.get()
    if outer is None:
        transcript.append(request, response, effects=(effect,))
    else:
        outer.append(effect)


def _body(data: bytes, *, decode_json=True):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    if not decode_json:
        return text
    try:
        return json.loads(text)
    except ValueError:
        return text


class PublicTranscriptMiddleware:
    """Observe ASGI requests and responses without replacing validation or errors.

    Headers created by the ASGI application are recorded; network/proxy headers
    and timing are outside scope. Request credentials are deliberately not logged.
    Only body bytes actually consumed by the application are relevant input here.
    """

    def __init__(self, app, transcript: PublicTranscript, max_body_bytes=2 * 1024 * 1024):
        self.app = app
        self.transcript = transcript
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_body = bytearray()
        response_body = bytearray()
        effects: list[dict] = []
        token = BOUNDARY.set(effects)
        complete = True
        response_complete = False
        status = None
        headers = []

        def retain(buffer, chunk):
            nonlocal complete
            room = max(0, self.max_body_bytes - len(buffer))
            buffer.extend(chunk[:room])
            if len(chunk) > room:
                complete = False

        async def read():
            message = await receive()
            if message["type"] == "http.request":
                retain(request_body, message.get("body", b""))
            return message

        async def write(message):
            nonlocal status, headers, response_complete
            if message["type"] == "http.response.start":
                status = message["status"]
                headers = [
                    [k.decode("latin1"), v.decode("latin1")] for k, v in message.get("headers", ())
                ]
            elif message["type"] == "http.response.body":
                retain(response_body, message.get("body", b""))
            await send(message)
            if message["type"] == "http.response.body":
                response_complete = not message.get("more_body", False)

        try:
            await self.app(scope, read, write)
        finally:
            BOUNDARY.reset(token)
            path = scope["path"]
            self.transcript.append(
                {
                    "operation": (
                        "evidence"
                        if "/evidence/" in path
                        else "action"
                        if path.endswith("/actions")
                        else path.rstrip("/").split("/")[-1]
                    ),
                    "method": scope["method"],
                    "path": path,
                    "query": scope.get("query_string", b"").decode("latin1"),
                    "body": _body(bytes(request_body)),
                    "content_type": [
                        v.decode("latin1")
                        for k, v in scope.get("headers", ())
                        if k.lower() == b"content-type"
                    ],
                },
                {
                    "status": status,
                    "headers": headers,
                    "body": _body(
                        bytes(response_body),
                        decode_json=any(
                            k.lower() == "content-type" and "application/json" in v.lower()
                            for k, v in headers
                        ),
                    ),
                },
                effects=effects,
                transport="http-asgi",
                complete=complete and response_complete,
            )
