"""Package the clean checkout's pinned pilot; no model calls.

Cross-axis packaging also uses the repository's installed mechanical qualifier.
"""

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_cross_axis_reports(root, runtime_source_sha256):
    """Revalidate the complete proof report before creating a release directory."""
    try:
        from nexus.evaluation.cross_axis import Pilot, validate_report
    except ImportError as exc:
        raise ValueError(
            "cross-axis packaging requires the repository's Python environment"
        ) from exc
    try:
        pilot = Pilot.model_validate_json((root / "docs/cross-axis-matrix.json").read_bytes())
        report = json.loads(
            (root / "docs/research/cross-axis-preflight-2026-10-29.json").read_bytes()
        )
    except (OSError, ValueError) as exc:
        raise ValueError("cross-axis matrix or preflight report cannot be read") from exc
    source_root = root / "src/nexus"
    sources = {
        path.relative_to(source_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source_root.rglob("*.py"))
    }
    if (
        not isinstance(report, dict)
        or not sources
        or report.get("sources") != sources
        or report.get("source_sha256") != runtime_source_sha256
    ):
        raise ValueError("cross-axis report source binding differs from the checkout or runtime")
    validate_report(pilot, report)


def validate_comparison_reports(root):
    """Check report completeness and provenance, not recompute their proofs.

    The packaged launcher still recomputes qualification inside the pinned image.
    This host-side guard uses only the standard library and never calls a model.
    """

    def require(condition, reason):
        if not condition:
            raise ValueError(f"comparison reports: {reason}")

    def read(name):
        try:
            value = json.loads((root / name).read_bytes())
        except (OSError, ValueError) as exc:
            raise ValueError(f"comparison reports: cannot read {name}") from exc
        require(isinstance(value, dict), f"{name} must contain an object")
        return value

    source_root = root / "src/nexus"
    sources = {
        path.relative_to(source_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source_root.rglob("*.py"))
    }
    require(bool(sources), "current Python source map is empty")
    matrix = read("docs/interference-matrix.json")
    matrix_digest = hashlib.sha256(
        json.dumps(matrix, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    preflight = read("docs/research/interference-comparison-preflight-2026-10-27.json")
    require(
        preflight.get("version") == "interference-comparison-preflight-v1"
        and preflight.get("status") == "passed"
        and "error" not in preflight,
        "comparison preflight must have passed",
    )
    require(preflight.get("sources") == sources, "comparison preflight source map is stale")
    require(preflight.get("matrix_sha256") == matrix_digest, "comparison matrix digest differs")
    expected_ids = [f"{index:02d}" for index in range(1, 33)]
    runs, cells = matrix.get("runs"), preflight.get("cells")
    for name, values in (("matrix", runs), ("preflight", cells)):
        require(
            isinstance(values, list)
            and all(isinstance(cell, dict) for cell in values)
            and [cell.get("id") for cell in values] == expected_ids,
            f"{name} must contain ordered unique rows 01..32",
        )
    checks = {
        "compiled_contract",
        "public_policy_supported_win",
        "exact_reference_actions",
        "exact_replay",
        "independent_optimum",
        "independent_restricted_baseline",
        "independent_coordinate_break_minimum",
        "paired_seed_kernel_and_target",
        "complete_transition_checks",
        "tool_limit_covers_allowance",
        "horizon_stratum_bound",
        "factorization_or_optimal_interleaving",
        "coupled_coordinate_regression_required",
    }
    structural_checks = {
        "independent_structural_costs",
        "coordinate_metric_matches_original",
        "block_cost_ordering",
        "live_structural_diagnostics",
    }
    for row, cell in zip(runs, cells, strict=True):
        require(all(cell.get(key) == value for key, value in row.items()), "row identity differs")
        for field, names in (("checks", checks), ("structural_checks", structural_checks)):
            actual = cell.get(field)
            require(
                isinstance(actual, dict)
                and set(actual) == names
                and all(value is True for value in actual.values()),
                f"row {cell['id']} has missing or failed {field}",
            )

    feasibility = read("docs/research/ternary-feasibility-2026-10-27.json")
    require(
        feasibility.get("version") == "ternary-feasibility-v1"
        and feasibility.get("status") == "completed"
        and "error" not in feasibility,
        "ternary feasibility must be completed",
    )
    require(feasibility.get("sources") == sources, "ternary feasibility source map is stale")
    seeds = [67, 79, 101, 103]
    variants = ["spill-ring", "boundary-crossguard", "all-crossguard", "self-guard"]
    require(
        feasibility.get("seeds") == seeds
        and feasibility.get("variants") == variants
        and feasibility.get("kernel_attempt_limit_per_seed") == 32
        and feasibility.get("state_bound") == 19683,
        "ternary feasibility scope differs",
    )
    require(
        feasibility.get("first_admission_gate") == {"minimum_machine_blocks": 16}
        and feasibility.get("second_admission_gate")
        == {"minimum_whole_bank_reopening_operations": 2},
        "ternary admission gates differ",
    )
    require(feasibility.get("live_tasks_exported") == 0, "ternary probe exported live tasks")
    kernels = feasibility.get("kernels")
    expected = {
        (seed, attempt, variant)
        for seed in seeds
        for attempt in range(1, 33)
        for variant in variants
    }
    require(
        isinstance(kernels, list)
        and len(kernels) == 512
        and all(isinstance(kernel, dict) for kernel in kernels),
        "ternary feasibility requires 512 completed kernel records",
    )
    identities = [(k.get("seed"), k.get("attempt"), k.get("variant")) for k in kernels]
    require(
        all(
            type(seed) is int and type(attempt) is int and isinstance(variant, str)
            for seed, attempt, variant in identities
        )
        and set(identities) == expected,
        "ternary kernel records are missing, duplicate or outside the probe scope",
    )
    first_count = second_count = 0
    for kernel in kernels:
        require(
            kernel.get("status", "completed") == "completed"
            and "error" not in kernel
            and kernel.get("independent_transition_checks") == 177147
            and kernel.get("coupled_transition_checks") == 177147
            and kernel.get("independent_block_oracle_agrees") is True,
            "ternary kernel has pending or incomplete independent proof checks",
        )
        targets, proofs = kernel.get("targets_passing_first_gate"), kernel.get("candidate_proofs")
        require(
            isinstance(targets, list)
            and all(type(state) is int and 0 <= state < 19683 for state in targets)
            and len(set(targets)) == len(targets)
            and isinstance(proofs, list)
            and len(proofs) == len(targets)
            and all(isinstance(proof, dict) for proof in proofs),
            "ternary candidate records are incomplete",
        )
        states = [proof.get("state") for proof in proofs]
        require(
            all(type(state) is int for state in states) and set(states) == set(targets),
            "ternary candidate proofs do not cover first-gate targets",
        )
        first_count += len(targets)
        for proof in proofs:
            target = proof.get("target")
            operations = proof.get("minimum_operations")
            blocks = proof.get("minimum_machine_blocks")
            reopenings = proof.get("minimum_whole_bank_reopening_operations")
            require(
                isinstance(target, list)
                and len(target) == 9
                and all(type(value) is int and value in (1, 2) for value in target)
                and sum(value * 3**index for index, value in enumerate(target)) == proof["state"]
                and type(operations) is int
                and type(blocks) is int
                and operations >= blocks >= 16
                and type(reopenings) is int
                and reopenings >= 0
                and proof.get("second_gate_passed") is (reopenings >= 2)
                and proof.get("status", "completed") == "completed"
                and "error" not in proof,
                "ternary candidate proof or gate result is incomplete",
            )
            second_count += int(proof["second_gate_passed"])
    require(
        type(feasibility.get("first_gate_candidate_count")) is int
        and feasibility["first_gate_candidate_count"] == first_count
        and type(feasibility.get("second_gate_candidate_count")) is int
        and feasibility["second_gate_candidate_count"] == second_count,
        "ternary gate totals differ from completed records",
    )
    require(
        second_count == 0 and feasibility.get("admission") == "no-target-passes-tested-gates",
        "comparison package requires a failed ternary gate with no runtime admission",
    )


def main(pilot_name="coordination"):
    if pilot_name not in (
        "coordination",
        "interference",
        "interference-comparison",
        "cross-axis",
        "capability-smoke",
    ):
        raise ValueError("unknown pilot profile")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runtime-source-sha256", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{64}", args.runtime_source_sha256):
        parser.error("runtime source SHA-256 must be 64 lowercase hexadecimal characters")
    git = ["git", "-C", str(ROOT)]
    if subprocess.check_output([*git, "status", "--porcelain"], text=True).strip():
        parser.error("commit or isolate checkout changes before packaging")
    commit = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    if pilot_name == "interference-comparison":
        try:
            validate_comparison_reports(ROOT)
        except ValueError as exc:
            parser.error(str(exc))
    if pilot_name in ("cross-axis", "capability-smoke"):
        try:
            validate_cross_axis_reports(ROOT, args.runtime_source_sha256)
        except ValueError as exc:
            parser.error(str(exc))
    examples = ROOT / "examples/mindtrial"
    spec = importlib.util.spec_from_file_location(
        "coordination_runner", examples / "coordination-runner.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the pilot launcher")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    profile = {
        "coordination": runner.COORDINATION,
        "interference": runner.INTERFERENCE,
        "interference-comparison": runner.INTERFERENCE_COMPARISON,
        "cross-axis": runner.CROSS_AXIS,
        "capability-smoke": runner.CAPABILITY_SMOKE,
    }[pilot_name]
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    copies = {
        "run.sh": examples / f"{pilot_name}-run.sh",
        "runner.py": examples / f"{pilot_name}-runner.py",
        "README.md": examples / f"{pilot_name}-run.md",
        **{name: examples / name for name in profile.configs},
        **{
            f"nexus-{pilot_name}-{suite}-tasks.yaml": examples
            / f"nexus-{pilot_name}-{suite}-tasks.yaml"
            for suite in profile.suites
        },
    }
    if pilot_name != "coordination":
        copies["pilot_runner.py"] = examples / "coordination-runner.py"
    if pilot_name in ("interference-comparison", "cross-axis", "capability-smoke"):
        copies["guide.md"] = ROOT / f"docs/{pilot_name}-guide.md"
        copies["summarize_results.py"] = examples / "summarize-pilot-results.py"
    if pilot_name == "capability-smoke":
        copies["matrix.json"] = ROOT / "docs/capability-smoke-matrix.json"
        copies["followup-matrix.md"] = ROOT / "docs/inference-diagnostic-matrix.md"
    for name, source in copies.items():
        shutil.copy2(source, destination / name)
    reports = destination / "reports"
    reports.mkdir()
    report_names = {
        "coordination": (
            "coordination-preflight-2026-10-25.json",
            "coordination-legacy-preflight-2026-10-25.json",
            "planning-resource-pilot-results-2026-10-25.md",
            "planning-resource-pilot-results-2026-10-25.json",
        ),
        "interference": (
            "interference-preflight-2026-10-26.json",
            "interference-implementation-validation-2026-10-26.md",
            "coordination-rerun-results-2026-10-26.md",
            "coordination-rerun-results-2026-10-26.json",
        ),
        "interference-comparison": (
            "interference-comparison-preflight-2026-10-27.json",
            "ternary-feasibility-2026-10-27.json",
            "interference-comparison-validation-2026-10-27.md",
        ),
        "capability-smoke": (
            "cross-axis-preflight-2026-10-29.json",
            "capability-smoke-validation-2026-10-31.md",
            "capability-controls-results-2026-10-31.md",
            "capability-controls-results-2026-10-31.json",
            "capability-text-output-controls-2026-10-31.md",
            "capability-text-output-controls-2026-10-31.json",
            "capability-screen-results-2026-10-31.md",
            "capability-screen-results-2026-10-31.json",
            "smaller-model-synthesis-2026-11-01.md",
            "capability-repeat-synthesis-2026-11-01.json",
            "inference-diagnostic-validation-2026-11-01.json",
            "smoke-findings-2026-10-31.md",
            "smoke-findings-2026-10-31.json",
        ),
        "cross-axis": (
            "cross-axis-preflight-2026-10-29.json",
            "cross-axis-validation-2026-10-29.md",
        ),
    }[pilot_name]
    for name in report_names:
        shutil.copy2(ROOT / "docs/research" / name, reports / name)
    if pilot_name == "capability-smoke":
        followup = destination / "followup-matrix.md"
        followup.write_text(followup.read_text().replace("(research/", "(reports/"))
        guide = destination / "guide.md"
        guide.write_text(
            guide.read_text()
            .replace(
                "research/smoke-findings-2026-10-31.md", "reports/smoke-findings-2026-10-31.md"
            )
            .replace("capability-smoke-matrix.json", "matrix.json")
            .replace("inference-diagnostic-matrix.md", "followup-matrix.md")
            .replace(
                "research/capability-controls-results-2026-10-31.md",
                "reports/capability-controls-results-2026-10-31.md",
            )
            .replace(
                "research/capability-text-output-controls-2026-10-31.md",
                "reports/capability-text-output-controls-2026-10-31.md",
            )
            .replace(
                "research/capability-screen-results-2026-10-31.md",
                "reports/capability-screen-results-2026-10-31.md",
            )
            .replace(
                "research/smaller-model-synthesis-2026-11-01.md",
                "reports/smaller-model-synthesis-2026-11-01.md",
            )
        )
        findings = reports / "smoke-findings-2026-10-31.md"
        findings.write_text(
            findings.read_text().replace("../capability-smoke-guide.md", "../guide.md")
        )
    release = {
        "source_commit": commit,
        "branch": runner.BRANCH,
        "image": profile.image,
        "runtime_source_sha256": args.runtime_source_sha256,
        "config_contract_sha256": {
            name: runner.config_contract_sha256(runner.read_json(destination / name))
            for name in profile.configs
        },
        "files_sha256": {
            path.relative_to(destination).as_posix(): runner.sha256(path.read_bytes())
            for path in sorted(destination.rglob("*"))
            if path.is_file()
        },
        "design_url": f"https://github.com/petmal/NEXUS/blob/{commit}/docs/{pilot_name}-guide.md",
    }
    if profile.tool_contract_version:
        release["tool_contracts"] = {
            name: runner.tool_contract(
                runner.read_json(destination / name), profile.tool_contract_version
            )
            for name in profile.configs
        }
    runner.write_json(destination / "release.json", release)
    runner.load_release(destination, profile)
    for name in profile.configs:
        runner.load_config(destination, release, name)
    archive = shutil.make_archive(str(destination), "zip", destination.parent, destination.name)
    print(archive)


if __name__ == "__main__":
    main()
