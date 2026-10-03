import json
from pathlib import Path
from urllib.parse import urlparse

from nexus.generator import generate_episode
from nexus.models import ACTION_ADAPTER
from nexus.protocol.session import PERFORMANCE_SCHEMA_URL, Session


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "performance-v1.schema.json"


def _assert_value_matches_schema(value, spec):
    expected_type = spec.get("type")
    if expected_type == "integer":
        assert isinstance(value, int) and not isinstance(value, bool)
        if "minimum" in spec:
            assert value >= spec["minimum"]
        if "maximum" in spec:
            assert value <= spec["maximum"]
    elif expected_type == "string":
        assert isinstance(value, str)
        if spec.get("format") == "uri":
            parsed = urlparse(value)
            assert parsed.scheme in {"http", "https"}
            assert parsed.netloc

    if "enum" in spec:
        assert value in spec["enum"]


def test_terminal_performance_matches_published_v1_schema_contract():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])

    episode = generate_episode(
        23023,
        discovery_level=2,
        planning_level=1,
        resource_pressure=1,
        verifier_secret="performance-schema-secret",
    )
    session = Session(episode)
    terminal = None
    for raw_action in episode.reference_plan:
        terminal = session.act(
            session.state.turn,
            ACTION_ADAPTER.validate_python(raw_action),
        )
        assert terminal.ok

    assert terminal is not None and terminal.performance is not None
    payload = terminal.performance.model_dump(mode="json", by_alias=True)

    assert set(payload) == set(schema["required"])
    assert payload["$schema"] == PERFORMANCE_SCHEMA_URL
    for name, spec in schema["properties"].items():
        _assert_value_matches_schema(payload[name], spec)


def test_performance_schema_url_is_immutable_and_versioned():
    assert "/6421ea6b00f8f4a682d7678d7a73e69493a34f0a/" in PERFORMANCE_SCHEMA_URL
    assert PERFORMANCE_SCHEMA_URL.endswith("/schemas/performance-v1.schema.json")
