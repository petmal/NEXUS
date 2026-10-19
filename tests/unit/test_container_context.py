"""Keep the image's explicit document COPY list aligned with its build context."""

from pathlib import Path
from shlex import split

ROOT = Path(__file__).parents[2]


def test_docker_copied_documents_are_in_build_context():
    copied = {
        source
        for line in (ROOT / "Dockerfile").read_text().splitlines()
        if line.startswith("COPY ")
        for source in split(line)[1:-1]
        if source.startswith("docs/")
    }
    rules = (ROOT / ".dockerignore").read_text().splitlines()
    for source in copied:
        assert (ROOT / source).is_file(), f"Missing COPY source: {source}"
    # This repository deliberately filters docs/* with explicit file exceptions.
    # Check the relationship, without hard-coding the current set of matrices.
    if "docs/*" in rules:
        allowed = {line[1:] for line in rules if line.startswith("!")}
        assert copied <= allowed, f"Documents excluded from build context: {copied - allowed}"
