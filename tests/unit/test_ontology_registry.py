"""Human-authored registrations are lazy, explicit and conflict checked."""

import json
import subprocess
import sys
from dataclasses import replace

import pytest
from typer.testing import CliRunner

from nexus.cli import app
from nexus.generator import generate_episode
from nexus.ontology.catalog import BUILTINS, OntologyRegistry
from nexus.ontology.payloads import schema_for


def test_duplicate_families_and_specifications_cannot_be_silently_overwritten():
    original = BUILTINS["model-revision-v1"]
    with pytest.raises(ValueError, match="duplicate ontology family"):
        OntologyRegistry.from_definitions([original, original])
    with pytest.raises(ValueError, match="duplicate specification"):
        OntologyRegistry.from_definitions([original, replace(original, family="another-v1")])
    with pytest.raises(ValueError, match="API version"):
        replace(original, api_version=2)
    with pytest.raises(ValueError, match="incomplete import"):
        replace(original, qualifier=("", ""))
    with pytest.raises(TypeError):
        BUILTINS["new-v1"] = original
    with pytest.raises(TypeError):
        original.schemas["truth"] = object


def test_schema_lookup_does_not_import_runtime_or_compile_prior():
    script = """
import sys
from nexus.ontology.payloads import schema_for
schema_for('model-revision-v1', 'artifact')
assert 'nexus.ontology.revision.runtime' not in sys.modules
assert 'nexus.ontology.revision.laws' not in sys.modules
assert 'nexus.ontology.stateful.schema' not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_missing_roles_and_legacy_model_selection_are_explicit():
    assert BUILTINS["shared-response-v1"].specification_version == "scientific-v2"
    assert not BUILTINS["shared-response-v1"].schemas
    with pytest.raises(ValueError, match="unsupported ontology payload"):
        schema_for("stateful-discovery-v1", "stock")
    with pytest.raises(ValueError, match="unsupported ontology payload"):
        schema_for("unregistered-v1", "artifact")
    invalid = replace(
        BUILTINS["model-revision-v1"], schema_module="nexus.ontology.discovery.schema"
    )
    with pytest.raises(ValueError, match="schemas require"):
        _ = invalid.schemas


def test_options_are_explicit_and_ontology_validated():
    with pytest.raises(ValueError, match="not supported"):
        generate_episode(
            0,
            axis_version=2,
            science_family="coupled-memory-v1",
            ontology_options={"guidance": "principles"},
        )
    with pytest.raises(ValueError, match="JSON object"):
        generate_episode(0, ontology_options=[])
    with pytest.raises(ValueError):
        generate_episode(
            0,
            axis_version=2,
            science_family="model-revision-v1",
            ontology_options={"unrecognized": True},
        )


def test_cli_lists_adapters_and_accepts_validated_options(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["ontologies", "--json"])
    assert result.exit_code == 0, result.stdout
    rows = {r["family"]: r for r in json.loads(result.stdout)}
    assert rows["model-revision-v1"]["schema_module"] == "nexus.ontology.revision.schema"
    assert not rows["categorical-chain-poc-v1"]["generatable"]
    common = [
        "generate",
        str(tmp_path),
        "--axis-version",
        "2",
        "--science-family",
        "model-revision-v1",
        "--theory-level",
        "3",
        "--discovery-level",
        "5",
        "--planning-level",
        "0",
    ]
    result = runner.invoke(app, [*common, "--ontology-options", '{"guidance":"principles"}'])
    assert result.exit_code == 0, result.stdout
    payload = json.loads((tmp_path / "private.json").read_text())
    assert payload["public"]["investigation"]["payload"]["provisional"] is None
    assert runner.invoke(app, [*common, "--ontology-options", "[]"]).exit_code != 0


def test_direct_registry_constructor_cannot_hide_a_specification_collision():
    original = BUILTINS["model-revision-v1"]
    other = replace(original, family="another-v1")
    with pytest.raises(ValueError, match="same unique definitions"):
        OntologyRegistry(
            {original.family: original, other.family: other},
            {original.specification_version: other},
        )


def test_standalone_action_contracts_work_before_an_episode_is_selected():
    from nexus.cli import app
    from typer.testing import CliRunner

    runner = CliRunner()
    for name, definition in BUILTINS.items():
        if definition.generator is None:
            continue
        result = runner.invoke(app, ["actions", "--axis-version", "2", "--science-family", name])
        assert result.exit_code == 0, (name, result.exception)
        assert "finish" in result.output
    contract = BUILTINS["model-revision-v1"].action_reference()
    assert "assistance" not in contract["ontology"]
    assert "recoverable while actions remain" not in contract["ontology"]["contract"]
