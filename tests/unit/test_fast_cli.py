import json
import subprocess
import sys

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

    assert fast_cli.main(
        ["request", "--request-file", str(request_file), "--url", "http://service:8000"]
    ) == 0
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

    assert fast_cli.main(
        ["validate", "--candidate-file", str(candidate_file), "--url", "http://service:8000"]
    ) == 0
    assert seen == {
        "candidate": " NX-ABCD \n",
        "url": "http://service:8000",
    }
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"correct": True, "title": "ok", "explanation": "ok"}
    prefix = "NEXUS terminal performance: "
    assert captured.err.startswith(prefix)
    assert json.loads(captured.err[len(prefix):]) == {
        "terminal_status": "won", "goal_satisfied": True,
    }


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
