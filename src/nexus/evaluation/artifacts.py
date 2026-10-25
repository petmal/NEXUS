"""Small shared utilities for strict offline evaluation artifacts."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def atomic_json(path: Path, value: Any) -> None:
    """Replace one operator-owned report after serializing it completely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
