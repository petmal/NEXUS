import json
import pytest
from pathlib import Path
from urllib.parse import urlparse

from nexus.generator import generate_episode
from nexus.models import ACTION_ADAPTER
from nexus.protocol.session import PERFORMANCE_SCHEMA_URL, Session


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "performance-v6.schema.json"


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
    elif expected_type == "boolean":
        assert isinstance(value, bool)
    elif expected_type == "array":
        assert isinstance(value, list)
        item_spec = spec.get("items", {})
        for item in value:
            _assert_value_matches_schema(item, item_spec)

    if "enum" in spec:
        assert value in spec["enum"]


@pytest.mark.parametrize("theory", [0, 1, 2, 3])
def test_terminal_performance_matches_published_v6_schema_contract(theory):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])

    episode = generate_episode(
        23023,
        theory_level=theory,
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
    payload = terminal.model_dump(mode="json")["performance"]

    assert set(payload) == set(schema["required"])
    assert payload["$schema"] == PERFORMANCE_SCHEMA_URL
    for name, spec in schema["properties"].items():
        _assert_value_matches_schema(payload[name], spec)


def test_performance_schema_url_is_immutable_and_versioned():
    assert "/50ea40636bf46313fe5eef46973527dec097d17a/" in PERFORMANCE_SCHEMA_URL
    assert PERFORMANCE_SCHEMA_URL.endswith("/schemas/performance-v6.schema.json")
