from __future__ import annotations

import base64
import hashlib
import hmac

from nexus.engine.canonical import canonical_bytes
from nexus.models.episode import PrivateEpisode


def victory_receipt(episode: PrivateEpisode) -> str:
    payload = {
        "protocol_version": episode.public.protocol_version,
        "episode_id": episode.public.episode_id,
        "goal": episode.public.goal.model_dump(mode="json"),
        "status": "VICTORY",
    }
    digest = hmac.new(
        episode.verifier_secret.encode("utf-8"), canonical_bytes(payload), hashlib.sha256
    ).digest()[:10]
    token = base64.b32encode(digest).decode("ascii").rstrip("=")
    return "NX-" + "-".join(token[i : i + 4] for i in range(0, len(token), 4))
