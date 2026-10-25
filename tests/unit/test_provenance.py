"""Artifact identity must retain the original byte-level coverage after extraction."""

import hashlib
import json
import subprocess
import sys

from nexus import provenance


def test_digest_covers_relative_python_and_json_bytes_only(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "__file__", str(tmp_path / "provenance.py"))
    (tmp_path / "nested").mkdir()
    (tmp_path / "a.py").write_bytes(b"x = 1\n")
    (tmp_path / "nested/b.json").write_bytes(b"{}\n")
    (tmp_path / "notes.md").write_bytes(b"ignored")
    values = [
        (name, hashlib.sha256((tmp_path / name).read_bytes()).hexdigest())
        for name in ("a.py", "nested/b.json")
    ]
    expected = hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()
    assert provenance.source_digest() == expected
    (tmp_path / "notes.md").write_bytes(b"changed")
    assert provenance.source_digest() == expected
    (tmp_path / "nested/b.json").write_bytes(b"{}\r\n")
    assert provenance.source_digest() != expected
    (tmp_path / "nested/b.json").unlink()
    assert provenance.source_digest() != expected


def test_shared_utilities_do_not_load_a_pilot_or_generator():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "from nexus.provenance import source_digest; "
            "from nexus.evaluation.artifacts import atomic_json, StrictModel; "
            "import sys; assert 'nexus.evaluation.matrix' not in sys.modules; "
            "assert 'nexus.generator' not in sys.modules",
        ],
        check=True,
    )
