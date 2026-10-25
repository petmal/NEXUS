"""Fail-closed qualification, matched interventions and exact export inventory."""

import json
from pathlib import Path

import pytest

from nexus.evaluation import td_cycle, td_export
from nexus.evaluation.td_cycle import Cycle, length_certificates
from nexus.ontology.revision.laws import class_id, prior_mask, selection, specification
from nexus.ontology.revision.qualification import QualificationLimit, minimum_certificate

MATRIX = Path("docs/td-cycle-matrix.json")
TEMPLATE = Path("examples/mindtrial/td-cycle-harness.json")


@pytest.fixture(scope="module")
def qualified(tmp_path_factory):
    cycle = Cycle.model_validate_json(MATRIX.read_text())
    output = tmp_path_factory.mktemp("qualified") / "preflight.json"
    report = td_cycle.preflight(cycle, output)
    return cycle, output, report


def test_corrected_coordinates_and_controls(qualified):
    _, _, report = qualified
    cells = report["cells"]
    assert [c["minimum_reading_only_certificate"] for c in cells[:3]] == [4, 4, 2]
    assert all(not c["old_hard_tier_admitted"] for c in cells[3:9])
    assert all(c["L_star"] == 5 for c in cells[3:5])
    assert all(c["L_star"] == 6 for c in cells[5:9])
    assert all(p["public_evidence_identical"] for p in report["rival_pairs"])
    assert cells[11]["public_policy"]["baseline"]["actions"] == 4
    assert len(cells[2]["certificate_queries"]) == 2
    assert cells[2]["C_by_maximum_query_length"][2] is None


def test_certificate_restriction_does_not_reuse_unrestricted_bound():
    world = selection(0)
    spec = specification(world, 3, 5)
    mask, truth = prior_mask(spec), class_id(world.program)
    values = length_certificates(mask, truth)
    assert minimum_certificate(mask, truth).readings == 4
    assert values[2]["readings"] == 5
    with pytest.raises(QualificationLimit):
        minimum_certificate(mask, truth, max_nodes=0)
    with pytest.raises(ValueError, match="distinct legal"):
        minimum_certificate(mask, truth, query_indices=(True,))
    with pytest.raises(ValueError, match="do not identify"):
        minimum_certificate(mask, truth, query_indices=())


def test_invalid_inventory_rejected():
    data = json.loads(MATRIX.read_text())
    data["cases"][6]["pair"] = None
    with pytest.raises(ValueError, match="incomplete rival"):
        Cycle.model_validate(data)


def test_failed_preflight_replaces_old_pass(tmp_path, monkeypatch):
    path = tmp_path / "report.json"
    path.write_text('{"status":"passed"}')
    cycle = Cycle.model_validate_json(MATRIX.read_text())
    monkeypatch.setattr(
        td_cycle, "prove", lambda: (_ for _ in ()).throw(ValueError("proof failed"))
    )
    with pytest.raises(ValueError, match="proof failed"):
        td_cycle.preflight(cycle, path)
    assert json.loads(path.read_text())["status"] == "blocked"


def test_export_exact_matched_inventory_and_assistance(qualified, tmp_path):
    cycle, preflight, _ = qualified
    manifest = td_export.export(cycle, preflight, TEMPLATE, tmp_path, image="nexus:verified-local")
    assert len(manifest["executions"]) == 40
    assert manifest["live_results"] == "not_run"
    assert len(json.loads((tmp_path / "run-ledger.json").read_text())["runs"]) == 40
    counts = {
        "baseline": 24,
        "single-shot": 10,
        "consistency-baseline": 2,
        "consistency-prompt": 2,
        "consistency-checker": 2,
    }
    for batch, count in counts.items():
        tasks = json.loads((tmp_path / f"{batch}-tasks.yaml").read_text())["task-config"]
        config = json.loads((tmp_path / f"{batch}-config.yaml").read_text())["config"]
        assert len(tasks["tasks"]) == count
        assert len(config["providers"]) == 1
        assert len(config["providers"][0]["runs"]) == 1
        assert all(
            item["image"] == "nexus:verified-local"
            for key in ("tools", "services", "validators")
            for item in config[key]
        )
        request = config["tools"][0]["parameters"]["properties"]["request"]
        assert ("check" in request["properties"]["operation"]["enum"]) == (
            batch == "consistency-checker"
        )
        for task in tasks["tasks"]:
            assert all(
                word not in task["prompt"].lower()
                for word in ("seed", "certificate", "rival", "hidden program")
            )
            inputs = task["tool-selector"]["service-inputs"]["nexus"]
            options = json.loads(inputs["ontology-options"])
            assert (options["finish_policy"] == "single") == (batch == "single-shot")
            assert (options["consistency_check"] == "readings") == (batch == "consistency-checker")
    baseline = json.loads((tmp_path / "consistency-baseline-tasks.yaml").read_text())[
        "task-config"
    ]["tasks"][0]
    prompt = json.loads((tmp_path / "consistency-prompt-tasks.yaml").read_text())["task-config"][
        "tasks"
    ][0]
    assert baseline["tool-selector"] == prompt["tool-selector"]
    assert prompt["prompt"].startswith(baseline["prompt"])


def test_export_rejects_stale_source_before_writing(qualified, tmp_path, monkeypatch):
    cycle, preflight, _ = qualified
    monkeypatch.setattr(td_export, "source_digest", lambda: "different")
    with pytest.raises(ValueError, match="source is stale"):
        td_export.export(cycle, preflight, TEMPLATE, tmp_path / "out", image="nexus:test")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "change",
    [
        "version",
        "proof",
        "empty-checks",
        "truthy-check",
        "missing-pair",
        "missing-replay",
        "case-identity",
    ],
)
def test_export_rejects_incomplete_qualification_artifacts(qualified, tmp_path, change):
    cycle, _, report = qualified
    data = json.loads(json.dumps(report))
    if change == "version":
        data["version"] = "wrong"
    elif change == "proof":
        data.pop("independent_proof")
    elif change == "missing-pair":
        data.pop("rival_pairs")
    elif change == "truthy-check":
        data["cells"][0]["checks"]["expected_C"] = "true"
    elif change == "empty-checks":
        data["cells"][0]["checks"] = {}
    elif change == "missing-replay":
        data["cells"][0]["public_policy"].pop("single-shot")
    else:
        data["cells"][0]["seed"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        td_export.export(cycle, path, TEMPLATE, tmp_path / "out", image="nexus:test")
    assert not (tmp_path / "out").exists()


def test_export_rejects_edited_harness_contract(qualified, tmp_path):
    cycle, preflight, _ = qualified
    template = json.loads(TEMPLATE.read_text())
    inputs = template["tasks"]["task-config"]["tasks"][0]["tool-selector"]["service-inputs"][
        "nexus"
    ]
    inputs["resource-pressure"] = 0
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(template))
    with pytest.raises(ValueError, match="source-pinned contract"):
        td_export.export(cycle, preflight, path, tmp_path / "out", image="nexus:test")


def test_balanced_triple_cannot_be_replaced_with_unrelated_world(tmp_path, monkeypatch):
    data = json.loads(MATRIX.read_text())
    data["cases"][0].update(seed=0, expected_horizon=3)
    data["cases"][11]["seed"] = 0
    cycle = Cycle.model_validate(data)
    monkeypatch.setattr(td_cycle, "prove", lambda: {"passed": True})
    output = tmp_path / "bad-triple.json"
    with pytest.raises(ValueError, match="balanced triple public evidence differs"):
        td_cycle.preflight(cycle, output)
    assert json.loads(output.read_text())["status"] == "blocked"
