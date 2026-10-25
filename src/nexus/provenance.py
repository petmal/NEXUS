"""Source identity shared by runtime journals and offline qualification.

A digest binds artifacts to installed bytes; it is not a proof of correctness.
Keep this module independent of generators and particular evaluation matrices.
"""

import hashlib
import json
from pathlib import Path


def source_digest() -> str:
    root = Path(__file__).resolve().parent
    values = [
        (p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
        for p in sorted(root.rglob("*"))
        if p.suffix in (".py", ".json")
    ]
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()
