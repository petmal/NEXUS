from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel


def canonical_bytes(value: BaseModel | dict | list | tuple) -> bytes:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(value: BaseModel | dict | list | tuple) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()
