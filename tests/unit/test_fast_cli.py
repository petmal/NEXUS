import json
import subprocess
import sys

import pytest

from nexus.protocol import fast_cli


def test_fast_request_command_reads_one_envelope(tmp_path, monkeypatch, capsys):
    request_file = tmp_path / "request.json"
    request_file.write_text('{"operation":"observe"}', encoding="utf-8")
    seen = {}

    def fake_request(request, *, url=None):
        seen["request"] = request
        seen["url"] = url
        return {"ok": True}

    monkeypatch.setattr(fast_cli, "request_service_payload", fake_request)

    assert (
        fast_cli.main(
            ["request", "--request-file", str(request_file), "--url", "http://service:8000"]
        )
        == 0
    )
    assert seen == {
        "request": {"operation": "observe"},
        "url": "http://service:8000",
    }
    assert json.loads(capsys.readouterr().out) == {"ok": True}


def test_fast_validate_command_accepts_candidate_file(tmp_path, monkeypatch, capsys):
    candidate_file = tmp_path / "candidate"
    candidate_file.write_text(" NX-ABCD \n", encoding="utf-8")
    seen = {}

    def fake_validate(candidate, *, url=None):
        seen["candidate"] = candidate
        seen["url"] = url
        return (
            {"correct": True, "title": "ok", "explanation": "ok"},
            {"terminal_status": "won", "goal_satisfied": True},
        )

    monkeypatch.setattr(fast_cli, "validate_candidate_payload_with_performance", fake_validate)

    assert (
        fast_cli.main(
            ["validate", "--candidate-file", str(candidate_file), "--url", "http://service:8000"]
        )
        == 0
    )
    assert seen == {
        "candidate": " NX-ABCD \n",
        "url": "http://service:8000",
    }
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"correct": True, "title": "ok", "explanation": "ok"}
    prefix = "NEXUS terminal performance: "
    assert captured.err.startswith(prefix)
    assert json.loads(captured.err.splitlines()[0][len(prefix) :]) == {
        "terminal_status": "won",
        "goal_satisfied": True,
    }
    classification = json.loads(
        captured.err.splitlines()[1].removeprefix("NEXUS receipt classification: ")
    )
    assert classification["classification"] == "accepted_receipt"


def test_fast_entrypoint_does_not_import_heavy_dependencies():
    script = r"""
import json
import sys

import nexus.protocol.fast_cli as fast_cli

fast_cli.check_health = lambda **_kwargs: None
sys.argv = ["nexus", "health"]

from nexus.entrypoint import main

try:
    main()
except SystemExit as exc:
    if exc.code != 0:
        raise

heavy = [
    name
    for name in ("networkx", "pydantic", "rich", "typer")
    if name in sys.modules
]
print(json.dumps(heavy))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.splitlines()[-1] == "[]"


def test_action_timeout_has_headroom_while_health_remains_fast(monkeypatch):
    from io import BytesIO

    from nexus.protocol import transport

    seen = []

    def serve(request, *, timeout):
        seen.append((request.full_url, timeout))
        if request.full_url.endswith("/status"):
            return BytesIO(
                b'{"turn":0,"status":"active","actions_remaining":43,"victory_code":null}'
            )
        if request.full_url.endswith("/health"):
            return BytesIO(b'{"status":"ok"}')
        return BytesIO(b'{"ok":true}')

    monkeypatch.setattr(transport, "urlopen", serve)
    assert transport.request_service_payload(
        {"operation": "action", "action": {"type": "finish"}}, url="http://nexus"
    ) == {"ok": True}
    transport.check_health(url="http://nexus")
    assert seen == [
        ("http://nexus/status", 10.0),
        ("http://nexus/action", 45.0),
        ("http://nexus/health", 1.0),
    ]


def test_missing_tool_file_gives_conditional_mapping_hint_without_service_contact(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(
        fast_cli,
        "request_service_payload",
        lambda *_args, **_kwargs: pytest.fail("service contacted"),
    )
    assert (
        fast_cli.main(
            ["request", "--request-file", str(tmp_path / "absent"), "--tool-argument", "request"]
        )
        == 2
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert '{"request":{"operation":"manifest"}}' in output.err
    assert "file mapping" in output.err
    assert "does not identify whether the argument or mapping is wrong" in output.err


@pytest.mark.parametrize(
    "payload", [[], {}, {"operation": None}, {"request": {"operation": "manifest"}}]
)
def test_invalid_request_file_is_not_normalized_or_sent(tmp_path, monkeypatch, capsys, payload):
    request_file = tmp_path / "request.json"
    request_file.write_text(json.dumps(payload))
    monkeypatch.setattr(
        fast_cli,
        "request_service_payload",
        lambda *_args, **_kwargs: pytest.fail("service contacted"),
    )
    assert (
        fast_cli.main(
            ["request", "--request-file", str(request_file), "--tool-argument", "request"]
        )
        == 2
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert "string 'operation' field" in output.err
    assert "inner request object" in output.err


def test_valid_tool_mapping_still_sends_only_inner_payload(tmp_path, monkeypatch, capsys):
    request_file = tmp_path / "request.json"
    request_file.write_text('{"operation":"manifest"}')
    calls = []
    monkeypatch.setattr(
        fast_cli,
        "request_service_payload",
        lambda payload, **kwargs: calls.append((payload, kwargs)) or {"episode_id": "test"},
    )
    assert (
        fast_cli.main(
            ["request", "--request-file", str(request_file), "--tool-argument", "request"]
        )
        == 0
    )
    assert calls == [({"operation": "manifest"}, {"url": None})]
    assert capsys.readouterr().err == ""


def test_standalone_missing_file_does_not_claim_tool_wrapper(tmp_path, capsys):
    assert fast_cli.main(["request", "--request-file", str(tmp_path / "absent")]) == 2
    error = capsys.readouterr().err
    assert "request failed:" in error
    assert "outer" not in error and "Tool arguments" not in error
