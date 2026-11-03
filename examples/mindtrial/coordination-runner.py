#!/usr/bin/env python3
"""Build, qualify and run the pinned pilot with the user's existing MindTrial.

Only Python 3.12+ and its standard library are needed on the host. Config and task
files use JSON, which is also valid YAML. No live model call occurs in preflight.
"""

import argparse
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

CONFIG = "nexus-coordination-config.yaml"
REPEAT_CONFIG = "nexus-coordination-repeat-config.yaml"
CONFIGS = (CONFIG, REPEAT_CONFIG)
EDITABLE_RUN_FIELDS = ("name", "model", "model-parameters", "max-requests-per-minute")
SUITES = ("core", "slack", "spatial", "repeat")
BRANCH = "feat/planning-resource-axes"
IMAGE = "nexus:coordination-v1"
PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "mistralai": "MISTRAL_API_KEY",
    "xai": "XAI_API_KEY",
}

# All generated files stay inside the container's temporary directory. Only JSON
# crosses stdout; there are no host mounts or container-owned result files.
PREFLIGHT_SCRIPT = r"""
import contextlib
import json
from pathlib import Path
from typing import NamedTuple
import sys
import tempfile
from nexus.evaluation.coordination import Pilot, export_tasks, preflight
from nexus.provenance import source_digest

with contextlib.redirect_stdout(sys.stderr), tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    pilot = Pilot.model_validate_json(Path("/app/docs/coordination-matrix.json").read_text())
    report = preflight(pilot, directory / "coordination-preflight.json")
    export_tasks(pilot, report, directory)
    reports = {"coordination": report}
    suites = ["core", "slack", "spatial"]
    if "--repeat" in sys.argv[1:]:
        from nexus.evaluation.coordination import export_repeat_tasks
        export_repeat_tasks(directory)
        reports["planning_repeat"] = json.loads(
            (directory / "planning-repeat-preflight.json").read_text()
        )
        suites.append("repeat")
    result = {
        "runtime_source_sha256": source_digest(),
        "reports": reports,
        "tasks": {
            suite: json.loads((directory / f"nexus-coordination-{suite}-tasks.yaml").read_text())
            for suite in suites
        },
    }
print(json.dumps(result, separators=(",", ":")))
"""


class PilotProfile(NamedTuple):
    name: str
    image: str
    suites: tuple[str, ...]
    configs: tuple[str, ...]
    preflight_script: str
    suite_configs: tuple[tuple[str, str], ...] = ()
    suite_groups: tuple[tuple[str, tuple[str, ...]], ...] = ()
    default_suite: str = "core"
    tool_contract_version: str | None = None
    model_configs: tuple[tuple[str, str], ...] = ()
    evaluation_seed: str | None = None
    control_suite: str | None = None
    ungated_suites: tuple[str, ...] = ()
    proof_report: str | None = None


COORDINATION = PilotProfile("coordination", IMAGE, SUITES, CONFIGS, PREFLIGHT_SCRIPT)
INTERFERENCE = PilotProfile(
    "interference",
    "nexus:interference-v1",
    ("core", "slack"),
    ("nexus-interference-config.yaml",),
    r"""
import contextlib
import json
from pathlib import Path
import sys
import tempfile
from nexus.evaluation.interference import Pilot, export_tasks, preflight
from nexus.provenance import source_digest
with contextlib.redirect_stdout(sys.stderr), tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    pilot = Pilot.model_validate_json(Path("/app/docs/interference-matrix.json").read_text())
    report = preflight(pilot, directory / "interference-preflight.json")
    export_tasks(pilot, report, directory)
    result = {
        "runtime_source_sha256": source_digest(),
        "reports": {"interference": report},
        "tasks": {suite: json.loads((directory / f"nexus-interference-{suite}-tasks.yaml").read_text())
                  for suite in ("core", "slack")},
    }
print(json.dumps(result, separators=(",", ":")))
""",
)
INTERFERENCE_COMPARISON = PilotProfile(
    "interference-comparison",
    "nexus:interference-comparison-v1",
    ("core", "slack"),
    ("nexus-interference-comparison-config.yaml",),
    r"""
import contextlib
import json
from pathlib import Path
import sys
import tempfile
from nexus.evaluation.interference import Pilot
from nexus.evaluation.interference_comparison import export_tasks, preflight
from nexus.provenance import source_digest
with contextlib.redirect_stdout(sys.stderr), tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    pilot = Pilot.model_validate_json(Path("/app/docs/interference-matrix.json").read_text())
    report = preflight(pilot, directory / "interference-comparison-preflight.json")
    export_tasks(pilot, report, directory)
    result = {
        "runtime_source_sha256": source_digest(),
        "reports": {"interference-comparison": report},
        "tasks": {
            suite: json.loads(
                (directory / f"nexus-interference-comparison-{suite}-tasks.yaml").read_text()
            )
            for suite in ("core", "slack")
        },
    }
print(json.dumps(result, separators=(",", ":")))
""",
)
CROSS_AXIS_SUITES = (
    "canary-core",
    "canary-slack",
    "rerun-core",
    "rerun-slack",
    "smoke-td",
    "smoke-pr",
)
CROSS_AXIS_CONFIGS = (
    "nexus-cross-axis-canary-config.yaml",
    "nexus-cross-axis-rerun-config.yaml",
    "nexus-cross-axis-smoke-config.yaml",
)
CROSS_AXIS = PilotProfile(
    "cross-axis",
    "nexus:cross-axis-v1",
    CROSS_AXIS_SUITES,
    CROSS_AXIS_CONFIGS,
    r"""
import contextlib
import json
from pathlib import Path
import sys
import tempfile
from nexus.evaluation.cross_axis import Pilot, export_tasks, preflight
from nexus.provenance import source_digest
with contextlib.redirect_stdout(sys.stderr), tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    pilot = Pilot.model_validate_json(Path("/app/docs/cross-axis-matrix.json").read_text())
    report = preflight(pilot, directory / "cross-axis-preflight.json")
    export_tasks(pilot, report, directory)
    result = {
        "runtime_source_sha256": source_digest(),
        "reports": {"cross-axis": report},
        "tasks": {
            suite: json.loads((directory / f"nexus-cross-axis-{suite}-tasks.yaml").read_text())
            for suite in (
                "canary-core", "canary-slack", "rerun-core", "rerun-slack", "smoke-td", "smoke-pr"
            )
        },
    }
print(json.dumps(result, separators=(",", ":")))
""",
    tuple((suite, CROSS_AXIS_CONFIGS[index // 2]) for index, suite in enumerate(CROSS_AXIS_SUITES)),
    (
        ("canary", CROSS_AXIS_SUITES[:2]),
        ("rerun", CROSS_AXIS_SUITES[2:4]),
        ("smoke", CROSS_AXIS_SUITES[4:]),
        ("followup", CROSS_AXIS_SUITES[2:]),
    ),
    "canary",
    "cross-axis-tools-v1",
)


# Reuse the full source-bound qualifier; select unchanged task objects only after
# export. Selection occurs inside the network-disabled container as well as on host.
CAPABILITY_SELECTION = {
    "controls": {"smoke-td": ("S05", "S21")},
    "screen": {
        "canary-core": ("09", "11"),
        "canary-slack": ("25", "27"),
        "smoke-td": ("S01", "S02", "S03", "S08", "S22", "S23", "S24"),
        "smoke-pr": ("S13", "S16", "S17"),
    },
}
CAPABILITY_MODELS = ("glm", "muse", "minimax", "mistral", "grok")
CAPABILITY_CONFIGS = tuple(
    f"nexus-capability-smoke-{model}-config.yaml" for model in CAPABILITY_MODELS
)


def select_capability_tasks(exports):
    """Keep task names, player text, inputs and harness limits exactly unchanged."""
    selected = {}
    for suite, sources in CAPABILITY_SELECTION.items():
        selected[suite] = copy.deepcopy(exports["smoke-td"])
        target = selected[suite]["task-config"]
        target["tasks"] = []
        for source, ids in sources.items():
            config = exports[source]["task-config"]
            if {k: v for k, v in config.items() if k != "tasks"} != {
                k: v for k, v in target.items() if k != "tasks"
            }:
                raise ValueError("Selected suites must have identical harness contracts")
            for row_id in ids:
                matches = [task for task in config["tasks"] if task["name"].endswith("-" + row_id)]
                if len(matches) != 1:
                    raise ValueError(f"Expected exactly one source task for {source}/{row_id}")
                target["tasks"].append(copy.deepcopy(matches[0]))
    return selected


# The small pure selector is also embedded in the container command. No new
# runtime package or Docker file is needed; all player-world source stays fixed.
_CAPABILITY_SELECTOR_SOURCE = inspect.getsource(select_capability_tasks)
CAPABILITY_SMOKE = PilotProfile(
    "capability-smoke",
    "nexus:capability-smoke-v1",
    ("controls", "screen"),
    CAPABILITY_CONFIGS,
    CROSS_AXIS.preflight_script.replace(
        'print(json.dumps(result, separators=(",", ":")))',
        "import copy\nCAPABILITY_SELECTION = "
        + repr(CAPABILITY_SELECTION)
        + "\n"
        + _CAPABILITY_SELECTOR_SOURCE
        + '\nresult["tasks"] = select_capability_tasks(result["tasks"])'
        + '\nresult["reports"]["capability-smoke"] = result["reports"].pop("cross-axis")'
        + '\nprint(json.dumps(result, separators=(",", ":")))',
    ),
    default_suite="controls",
    tool_contract_version="cross-axis-tools-v1",
    model_configs=tuple(zip(CAPABILITY_MODELS, CAPABILITY_CONFIGS)),
    evaluation_seed="nexus-cross-axis-pilot-v1",
)


FRESH_WORLD_MODELS = ("astra", "luna", "flash", "grok")
FRESH_WORLD_CONFIGS = tuple(f"nexus-fresh-world-{m}-config.yaml" for m in FRESH_WORLD_MODELS)
FRESH_WORLD = PilotProfile(
    "fresh-world", "nexus:fresh-world-v1",
    ("anchor", "controls", "td", "pr-a", "pr-b"), FRESH_WORLD_CONFIGS,
    r"""
import contextlib
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, "/app/scripts")
from fresh_worlds import Pilot, preflight, export_tasks, SUITES
from nexus.provenance import source_digest
with contextlib.redirect_stdout(sys.stderr), tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    pilot = Pilot.model_validate_json(Path("/app/docs/fresh-world-matrix.json").read_text())
    report = preflight(pilot, directory / "fresh-world-preflight.json")
    export_tasks(pilot, report, directory)
    result = {
        "runtime_source_sha256": source_digest(),
        "reports": {"fresh-world": report},
        "tasks": {suite: json.loads((directory / f"nexus-fresh-world-{suite}-tasks.yaml").read_text())
                  for suite in SUITES},
    }
print(json.dumps(result, separators=(",", ":")))
""",
    suite_groups=(("fresh", ("controls", "td", "pr-a", "pr-b")),
                  ("challenges", ("td", "pr-a", "pr-b"))),
    default_suite="controls", tool_contract_version="cross-axis-tools-v1",
    model_configs=tuple(zip(FRESH_WORLD_MODELS, FRESH_WORLD_CONFIGS)),
    evaluation_seed="nexus-cross-axis-pilot-v1", control_suite="controls",
    ungated_suites=("anchor",),
    proof_report="reports/fresh-world-preflight-2026-11-03.json",
)


class RunnerError(Exception):
    """An actionable failure safe to print without subprocess output or secrets."""


def timestamp():
    return datetime.now(UTC).isoformat()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    try:
        return json.loads(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise RunnerError(f"Cannot read valid JSON from {path.name}.") from exc


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def config_contract_sha256(config):
    """Hash the integration contract, excluding only documented provider-run choices.

    Release packaging uses this same function. Provider/run list structure,
    enabled flags, retry policies, task settings and the entire NEXUS integration
    remain in the digest. A tool's name or description is never an editable field.
    """
    contract = copy.deepcopy(config)
    settings = contract.get("config", {}) if isinstance(contract, dict) else {}
    providers = settings.get("providers", ()) if isinstance(settings, dict) else ()
    if isinstance(providers, list):
        for provider in providers:
            runs = provider.get("runs", ()) if isinstance(provider, dict) else ()
            if isinstance(runs, list):
                for run in runs:
                    if isinstance(run, dict):
                        for field in EDITABLE_RUN_FIELDS:
                            run.pop(field, None)
    return sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode())


def config_for_suite(suite, pilot=COORDINATION):
    if pilot.suite_configs:
        return dict(pilot.suite_configs)[suite]
    return pilot.configs[-1] if suite == "repeat" else pilot.configs[0]


def selected_suites(selection, pilot=COORDINATION):
    if selection == "all":
        return pilot.suites
    return dict(pilot.suite_groups).get(selection, (selection,))


def select_task_ids(exports, suites, task_ids):
    """Filter whole qualified task objects; reject typos and ambiguous suffixes."""
    if len(set(task_ids)) != len(task_ids):
        raise RunnerError("Each --task-id must be unique.")
    names = set()
    for task_id in task_ids:
        matches = [
            task["name"]
            for suite in suites
            for task in exports[suite]["task-config"]["tasks"]
            if task["name"] == task_id or task["name"].endswith("-" + task_id)
        ]
        if len(matches) != 1:
            raise RunnerError("Each --task-id must match exactly one task in the selected suites.")
        if matches[0] in names:
            raise RunnerError("Different --task-id values selected the same task.")
        names.add(matches[0])
    chosen = {}
    for suite in suites:
        value = copy.deepcopy(exports[suite])
        if task_ids:
            value["task-config"]["tasks"] = [
                task for task in value["task-config"]["tasks"] if task["name"] in names
            ]
        if value["task-config"]["tasks"]:
            chosen[suite] = value
    return chosen


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least one")
    return parsed


def tool_contract(config, version):
    """Identify the configured tool interface, not an observed provider wire schema."""
    fields = ("name", "description", "parameters", "parameter-files", "command")
    contract = [
        {key: tool[key] for key in fields if key in tool} for tool in config["config"]["tools"]
    ]
    return {
        "version": version,
        "scope": "configuration",
        "provider_wire_captured": False,
        "sha256": sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()),
    }


def require_credentials(configs):
    """Check only providers selected for this invocation, without exposing values."""
    required = set()
    for config, _ in configs.values():
        for provider in config["config"]["providers"]:
            if provider.get("disabled") is True or not any(
                run.get("disabled") is not True for run in provider["runs"]
            ):
                continue
            name = provider["name"]
            if name not in PROVIDER_KEYS:
                raise RunnerError("No environment-key mapping for a selected provider.")
            required.add(PROVIDER_KEYS[name])
    for variable in sorted(required):
        if not os.environ.get(variable, "").strip():
            raise RunnerError(f"Set {variable} before a model run; --preflight-only needs no key.")


def checked(command, *, label, **kwargs):
    """Capture administrative commands; never echo stderr that might hold a secret."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, **kwargs)
    except OSError as exc:
        raise RunnerError(f"{label} could not start ({type(exc).__name__}).") from exc
    if result.returncode:
        raise RunnerError(f"{label} failed (exit {result.returncode}).")
    return result.stdout


def load_release(package, pilot=COORDINATION):
    release = read_json(package / "release.json")
    if not isinstance(release, dict):
        raise RunnerError("release.json must contain an object.")
    if not re.fullmatch(r"[0-9a-f]{40}", str(release.get("source_commit", ""))):
        raise RunnerError("release.json must pin a full 40-character source commit.")
    if release.get("branch") != BRANCH or release.get("image") != pilot.image:
        raise RunnerError("release.json names an unexpected branch or image.")
    if not re.fullmatch(r"[0-9a-f]{64}", str(release.get("runtime_source_sha256", ""))):
        raise RunnerError("release.json must pin the runtime source digest.")
    hashes = release.get("files_sha256")
    required = {
        *pilot.configs,
        *(f"nexus-{pilot.name}-{suite}-tasks.yaml" for suite in pilot.suites),
    }
    if pilot.proof_report:
        required.add(pilot.proof_report)
    if not isinstance(hashes, dict) or not required <= hashes.keys():
        raise RunnerError("release.json must list all configs and every suite's task checksum.")
    contracts = release.get("config_contract_sha256")
    if (
        not isinstance(contracts, dict)
        or set(contracts) != set(pilot.configs)
        or any(not re.fullmatch(r"[0-9a-f]{64}", str(value)) for value in contracts.values())
    ):
        raise RunnerError("release.json must pin a config contract checksum for each config.")
    if pilot.tool_contract_version:
        tools = release.get("tool_contracts")
        if (
            not isinstance(tools, dict)
            or set(tools) != set(pilot.configs)
            or any(
                not isinstance(value, dict)
                or value.get("version") != pilot.tool_contract_version
                or value.get("scope") != "configuration"
                or value.get("provider_wire_captured") is not False
                or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", "")))
                for value in tools.values()
            )
        ):
            raise RunnerError("release.json must pin every configuration-level tool contract.")
    for name, digest in hashes.items():
        if (
            not isinstance(name, str)
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or not re.fullmatch(r"[0-9a-f]{64}", str(digest))
        ):
            raise RunnerError("release.json contains an invalid file checksum entry.")
        path = (package / name).resolve()
        if not path.is_relative_to(package) or not path.is_file():
            raise RunnerError("A release file is missing or outside the package.")
        # Model and reasoning-effort edits are deliberate and recorded per run.
        if name not in pilot.configs and sha256(path.read_bytes()) != digest:
            raise RunnerError(f"Release checksum mismatch: {name}.")
    return release


def load_config(package, release, filename=CONFIG):
    raw = (package / filename).read_bytes()
    config = read_json(package / filename)

    def reject_keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "api-key" and item is not None and str(item).strip():
                    raise RunnerError("Remove the embedded api-key; use provider environment keys.")
                reject_keys(item)
        elif isinstance(value, list):
            for item in value:
                reject_keys(item)

    reject_keys(config)
    for variable in PROVIDER_KEYS.values():
        secret = os.environ.get(variable, "")
        if secret and secret.encode() in raw:
            raise RunnerError(f"The config contains {variable}; remove it before running.")
    if not isinstance(config, dict) or not isinstance(config.get("config"), dict):
        raise RunnerError("The config file must contain a config object.")
    if config_contract_sha256(config) != release["config_contract_sha256"][filename]:
        raise RunnerError(
            f"Config contract mismatch: {filename}; only provider-run model, name, "
            "model-parameters and max-requests-per-minute may be edited."
        )
    for provider in config["config"]["providers"]:
        for run in provider["runs"]:
            if not isinstance(run.get("model"), str) or not run["model"].strip():
                raise RunnerError("Every provider run must name a nonblank model.")
            if "name" in run and not isinstance(run["name"], str):
                raise RunnerError("Provider run names must be strings.")
            if "model-parameters" in run and not isinstance(run["model-parameters"], dict):
                raise RunnerError("Provider run model-parameters must be an object.")
            if "max-requests-per-minute" in run and (
                type(run["max-requests-per-minute"]) is not int
                or run["max-requests-per-minute"] < 1
            ):
                raise RunnerError(
                    "Provider run max-requests-per-minute must be a positive integer."
                )
    for section in ("tools", "services", "validators"):
        entries = config["config"].get(section)
        if (
            not isinstance(entries, list)
            or not entries
            or any(
                not isinstance(item, dict) or item.get("image") != release["image"]
                for item in entries
            )
        ):
            raise RunnerError(f"Every {section} image must match the pinned release image.")
    expected_tool = release.get("tool_contracts", {}).get(filename)
    if (
        expected_tool is not None
        and tool_contract(config, expected_tool["version"]) != expected_tool
    ):
        raise RunnerError(f"Configuration-level tool contract mismatch: {filename}.")
    return config, raw


def build_image(repository, release):
    if not repository.is_dir():
        raise RunnerError(f"NEXUS_REPO does not exist: {repository}")
    git = ["git", "-C", str(repository)]
    checked([*git, "rev-parse", "--show-toplevel"], label="Opening NEXUS_REPO")
    commit = release["source_commit"]

    def has_commit():
        output = checked(
            [*git, "cat-file", "--batch-check"],
            label="Checking release commit",
            input=commit + "\n",
        ).strip()
        if output == f"{commit} missing":
            return False
        if not re.fullmatch(re.escape(commit) + r" commit [0-9]+", output):
            raise RunnerError("The pinned source object is not a commit.")
        return True

    if not has_commit():
        checked(
            [*git, "fetch", "--no-tags", "origin", release["branch"]],
            label="Fetching the release branch",
        )
        if not has_commit():
            raise RunnerError("The exact release commit is unavailable after fetching its branch.")
    with tempfile.TemporaryDirectory(prefix="nexus-coordination-build-") as temporary:
        directory = Path(temporary)
        archive = directory / "source.tar"
        checked(
            [*git, "archive", "--format=tar", f"--output={archive}", commit],
            label="Archiving the release commit",
        )
        source = directory / "source"
        source.mkdir()
        with tarfile.open(archive) as contents:
            contents.extractall(source, filter="data")
        checked(
            [
                "docker",
                "build",
                "--build-arg",
                f"VCS_REF={commit}",
                "-t",
                release["image"],
                str(source),
            ],
            label="Building the pinned NEXUS image",
        )


def inspect_image(release):
    output = checked(
        ["docker", "image", "inspect", release["image"], "--format", "{{json .}}"],
        label="Inspecting the NEXUS image",
    )
    try:
        info = json.loads(output)
        revision = info["Config"]["Labels"]["org.opencontainers.image.revision"]
        image_id = info["Id"]
    except (ValueError, KeyError, TypeError) as exc:
        raise RunnerError("The NEXUS image lacks an OCI revision or image ID.") from exc
    if revision != release["source_commit"]:
        raise RunnerError(
            "NEXUS image revision differs from release.json; rebuild without --skip-build."
        )
    # Docker prefixes the digest; Podman's compatible CLI can return bare hex.
    # Preserve the engine's immutable reference for execution and audit records.
    if not isinstance(image_id, str) or not re.fullmatch(r"(?:sha256:)?[0-9a-f]{64}", image_id):
        raise RunnerError("Docker returned an invalid image ID.")
    return {"tag": release["image"], "id": image_id, "revision": revision}


def qualify(package, release, image, include_repeat, *, pilot=COORDINATION):
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--entrypoint",
        "python",
        image["id"],
        "-c",
        pilot.preflight_script,
    ]
    if include_repeat:
        command.append("--repeat")
    output = checked(command, label="Container qualification")
    try:
        result = json.loads(output)
    except ValueError as exc:
        raise RunnerError("Container qualification did not return valid JSON.") from exc
    if (
        not isinstance(result, dict)
        or result.get("runtime_source_sha256") != release["runtime_source_sha256"]
    ):
        raise RunnerError("Installed runtime source digest differs from release.json.")
    required_reports = (pilot.name, "planning_repeat") if include_repeat else (pilot.name,)
    reports = result.get("reports")
    if not isinstance(reports, dict) or any(
        not isinstance(reports.get(name), dict) or reports[name].get("status") != "passed"
        for name in required_reports
    ):
        raise RunnerError("The container did not pass all required qualification reports.")
    if pilot.proof_report:
        expected = read_json(package / pilot.proof_report)
        actual = copy.deepcopy(reports[pilot.name])
        expected.pop("seconds", None)
        actual.pop("seconds", None)
        if actual != expected:
            raise RunnerError("Recomputed proof differs from the release-bound report.")
    tasks = result.get("tasks")
    for suite in pilot.suites if include_repeat else (s for s in pilot.suites if s != "repeat"):
        shipped = read_json(package / f"nexus-{pilot.name}-{suite}-tasks.yaml")
        if not isinstance(tasks, dict) or tasks.get(suite) != shipped:
            raise RunnerError(f"Shipped {suite} tasks differ from freshly qualified exports.")
    return result


def result_directory(package, suite):
    results = package / "results"
    results.mkdir(exist_ok=True)
    if results.resolve() != results:
        raise RunnerError("The package results directory must not be a symlink.")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return Path(tempfile.mkdtemp(prefix=f"{suite}-{stamp}-", dir=results))


def result_coverage(directory, config, tasks):
    """Check completed result slots, not mission success or receipt correctness.

    MindTrial can exit zero after cancellation with an empty JSON file. An
    unattended batch must not treat that as complete or continue silently.
    """
    expected = {
        (provider["name"], run.get("name") or run["model"], task["name"])
        for provider in config["config"]["providers"]
        if provider.get("disabled") is not True
        for run in provider["runs"]
        if run.get("disabled") is not True
        for task in tasks["task-config"]["tasks"]
        if task.get("disabled") is not True
    }
    result = {"expected": len(expected), "recorded": 0, "complete": False}
    path = directory / "mindtrial.json"
    if not path.is_file() or not path.stat().st_size:
        return {**result, "reason": "missing_or_empty_results"}
    try:
        payload = json.loads(path.read_bytes())
        providers = payload["Results"]
        if not isinstance(providers, dict):
            raise TypeError("Results must be an object")
        seen = Counter()
        traces = set()
        for provider, records in providers.items():
            if not isinstance(records, list):
                raise TypeError("Provider results must be a list")
            for record in records:
                if record["Kind"] not in ("Passed", "Failed", "Error", "Skipped"):
                    raise ValueError("Unknown result kind")
                key = (provider, record["Run"], record["Task"])
                if not all(isinstance(value, str) and value for value in key):
                    raise TypeError("Result identities must be nonempty strings")
                trace = record["TraceID"]
                if not isinstance(trace, str) or not trace or trace in traces:
                    raise ValueError("Missing or duplicate trace identity")
                traces.add(trace)
                seen[key] += 1
    except (OSError, ValueError, KeyError, TypeError):
        return {**result, "reason": "invalid_results"}
    complete = set(seen) == expected and all(count == 1 for count in seen.values())
    return {
        **result,
        "recorded": sum(seen.values()),
        "complete": complete,
        "reason": "complete" if complete else "incomplete_or_unexpected_selection",
        "missing": [list(key) for key in sorted(expected - seen.keys())],
        "unexpected": [list(key) for key in sorted(seen.keys() - expected)],
        "duplicate_conditions": [list(key) for key, count in sorted(seen.items()) if count > 1],
    }


def rate_limited_results(directory):
    """Recognize recorded HTTP 429 errors without treating world losses as outages."""
    try:
        payload = json.loads((directory / "mindtrial.json").read_text())
        return [
            {"provider": provider, "task": record["Task"], "trace_id": record["TraceID"]}
            for provider, records in payload["Results"].items()
            for record in records
            if record.get("Kind") == "Error"
            and re.search(
                r"\b429\s+Too Many Requests\b",
                (record.get("Details", {}).get("Error") or {}).get("Message", ""),
                re.IGNORECASE,
            )
        ]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        # Invalid/missing records are handled by coverage checks, not invented 429s.
        return []


def control_admission(package, release, config_name, config_raw, binary, tasks, *, pilot):
    """Latest matching result per control must pass before this model's challenges.

    This is an operational receipt/configuration gate, not an offline replay audit.
    Partial reruns may fill the record; a newer failure overrides an older pass.
    Different release, binary or inference settings cannot inherit admission.
    """
    expected = {task["name"]: task for task in tasks["task-config"]["tasks"]}
    filename = package / "summarize_results.py"
    if not filename.is_file():
        filename = package / "summarize-pilot-results.py"
    spec = importlib.util.spec_from_file_location("nexus_gate_readout", filename)
    if spec is None or spec.loader is None:
        raise RunnerError("Cannot load the control configuration checker.")
    readout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(readout)
    current = json.loads(config_raw)
    configured = {
        (p["name"], r.get("name") or r["model"]): (r, p.get("retry-policy", {}))
        for p in current["config"]["providers"] for r in p["runs"]
        if p.get("disabled") is not True and r.get("disabled") is not True
    }
    if len(configured) != 1:
        raise RunnerError("Control admission requires one configured model per file.")
    binary_hash = sha256(binary.read_bytes())
    candidates = []
    for path in (package / "results").glob(f"{pilot.control_suite}-*/manifest.json"):
        try:
            manifest = json.loads(path.read_bytes())
        except (OSError, ValueError):
            continue
        if isinstance(manifest, dict) and all(manifest.get(k) == v for k, v in {
            "suite": pilot.control_suite, "source_commit": release["source_commit"],
            "runtime_source_sha256": release["runtime_source_sha256"],
            "input_config_file": config_name, "input_config_sha256": sha256(config_raw),
            "mindtrial_sha256": binary_hash,
            "evaluation_seed": pilot.evaluation_seed,
        }.items()):
            candidates.append((str(manifest.get("started_at", "")), path, manifest))
    latest = {}
    for _, path, manifest in sorted(candidates, key=lambda entry: (entry[0], str(entry[1])), reverse=True):
        selection = manifest.get("selection")
        selected = selection.get("task_names") if isinstance(selection, dict) else None
        if (not isinstance(selected, list) or not selected
                or any(not isinstance(name, str) for name in selected)
                or len(set(selected)) != len(selected) or not set(selected) <= expected.keys()):
            raise RunnerError("A matching control manifest has an invalid task selection; inspect "
                              "the controls result folders before continuing.")
        pending = set(selected) - latest.keys()
        if not pending:
            continue
        folder = path.parent
        accepted = {}
        try:
            selected_tasks = read_json(folder / "tasks.yaml")
            effective = read_json(folder / "config.yaml")
            records = read_json(folder / "mindtrial.json")["Results"]
            valid = (
                manifest.get("status") == "completed"
                and manifest.get("exit_code") == manifest.get("launcher_exit_code") == 0
                and sha256((folder / "input-config.yaml").read_bytes()) == sha256(config_raw)
                and sha256((folder / "config.yaml").read_bytes()) == manifest["effective_config_sha256"]
                and sha256((folder / "tasks.yaml").read_bytes()) == manifest["tasks_sha256"]
                and selected_tasks == {"task-config": {
                    **tasks["task-config"], "tasks": [expected[name] for name in selected]}}
                and result_coverage(folder, effective, selected_tasks)["complete"]
            )
            for provider, values in records.items():
                for record in values:
                    run, retries = configured[(provider, record["Run"])]
                    snapshot = record.get("RunConfig", {})
                    accepted[record["Task"]] = (
                        valid and record["Kind"] == "Passed"
                        and record.get("Evaluation", {}).get("Seed") == pilot.evaluation_seed
                        and snapshot.get("Model") == run["model"]
                        and not readout.run_config_differences(run, snapshot, retries)
                        and record.get("Details", {}).get("Validation", {}).get("Title")
                        == "Valid victory code"
                    )
            result_hash = sha256((folder / "mindtrial.json").read_bytes())
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RunnerError):
            accepted, result_hash = {}, None
        for name in pending:
            latest[name] = {"task": name, "accepted": accepted.get(name, False),
                            "manifest": str(path), "manifest_sha256": sha256(path.read_bytes()),
                            "results_sha256": result_hash}
        if latest.keys() == expected.keys():
            break
    missing = sorted(name for name in expected if not latest.get(name, {}).get("accepted"))
    if missing:
        raise RunnerError(
            "Fresh control admission missing or failed for " + ", ".join(missing)
            + ". Run --suite controls for this model/settings, then resume --suite challenges."
        )
    return {"scope": "accepted receipts and matching recorded configuration; not canonical replay",
            "controls": [latest[name] for name in expected]}


def run_suite(
    package,
    suite,
    config,
    config_raw,
    release,
    image,
    preflight,
    mindtrial,
    invoked,
    *,
    pilot=COORDINATION,
    input_config_file=None,
    interactive=True,
    task_ids=(),
    repetition=1,
    repetitions=1,
    admission=None,
):
    binary = mindtrial / "mindtrial"
    binary_hash = sha256(binary.read_bytes())
    directory = result_directory(package, suite)
    tasks_path = directory / "tasks.yaml"
    config_path = directory / "config.yaml"
    # Use the exact compared export even if someone edits the package mid-run.
    selected = select_task_ids(preflight["tasks"], (suite,), task_ids)[suite]
    write_json(tasks_path, selected)
    (directory / "input-config.yaml").write_bytes(config_raw)
    effective = copy.deepcopy(config)
    effective["config"].update(
        {
            "output-dir": str(directory),
            "log-file": str(directory / "mindtrial.log"),
            "task-source": str(tasks_path),
            "output-basename": "mindtrial",
        }
    )
    for section in ("tools", "services", "validators"):
        for entry in effective["config"][section]:
            entry["image"] = image["id"]
    write_json(config_path, effective)
    write_json(directory / "preflight.json", preflight)
    write_json(directory / "release.json", release)
    seed = pilot.evaluation_seed or (
        "nexus-pr-pilot-v1" if suite == "repeat" else f"nexus-{pilot.name}-pilot-v1"
    )
    input_config_file = input_config_file or config_for_suite(suite, pilot)
    command = [
        "./mindtrial",
        f"-config={config_path}",
        f"-tasks={tasks_path}",
        "--debug",
        f"--interactive={str(interactive).lower()}",
        "--json",
        f"--evaluation-seed={seed}",
        "run",
    ]
    manifest = {
        "version": f"{pilot.name}-run-v1",
        "suite": suite,
        "status": "running",
        "invocation_timestamp": invoked,
        "started_at": timestamp(),
        "source_commit": release["source_commit"],
        "source_branch": release["branch"],
        "runtime_source_sha256": preflight["runtime_source_sha256"],
        "image": image,
        "mindtrial_binary": str(binary.resolve()),
        "mindtrial_sha256": binary_hash,
        "cwd": str(mindtrial),
        "command": command,
        "interactive": interactive,
        "selection": {
            "requested_task_ids": list(task_ids),
            "task_names": [t["name"] for t in selected["task-config"]["tasks"]],
            "qualified_suite_task_names": [
                t["name"] for t in preflight["tasks"][suite]["task-config"]["tasks"]
            ],
        },
        "repetition": {"index": repetition, "count": repetitions},
        "evaluation_seed": seed,
        "input_config_file": input_config_file,
        "input_config_sha256": sha256(config_raw),
        "input_config_contract_sha256": config_contract_sha256(config),
        "input_config_matches_release": sha256(config_raw)
        == release["files_sha256"][input_config_file],
        "effective_config_sha256": sha256(config_path.read_bytes()),
        "tasks_sha256": sha256(tasks_path.read_bytes()),
        "output_dir": str(directory),
    }
    if pilot.tool_contract_version:
        manifest["tool_contract"] = tool_contract(config, pilot.tool_contract_version)
    if admission is not None:
        manifest["control_admission"] = admission
    manifest_path = directory / "manifest.json"
    write_json(manifest_path, manifest)
    print(f"Running {suite}; results: {directory}", flush=True)
    try:
        # Keep output visible. Unattended mode cannot block on terminal input.
        options = {} if interactive else {"stdin": subprocess.DEVNULL}
        completed = subprocess.run(command, cwd=mindtrial, check=False, **options)
        code = completed.returncode
        manifest.update(status="completed" if code == 0 else "failed", exit_code=code)
    except KeyboardInterrupt:
        code = 130
        manifest.update(status="interrupted", exit_code=code)
    except OSError as exc:
        code = 1
        manifest.update(status="failed_to_start", exit_code=code, error=type(exc).__name__)
    if code == 0 and not interactive:
        coverage = result_coverage(directory, effective, selected)
        manifest["result_coverage"] = coverage
        if not coverage["complete"]:
            manifest["status"] = "incomplete_results"
            code = 2
            print(
                "Unattended run did not produce the complete selected result set; "
                "stopping the batch. Preserve this results folder.",
                file=sys.stderr,
            )
    rate_limits = rate_limited_results(directory)
    if rate_limits:
        manifest["rate_limited_results"] = rate_limits
        if code == 0:
            manifest["status"] = "rate_limited"
            code = 2
        print(
            "HTTP 429 recorded; stopping before the next group or repetition. "
            "Preserve results and resolve the provider limit before a new attempt.",
            file=sys.stderr,
        )
    manifest["launcher_exit_code"] = code if code >= 0 else 128 - code
    manifest["finished_at"] = timestamp()
    write_json(manifest_path, manifest)
    return manifest["launcher_exit_code"]


def main(argv=None, *, package_dir=None, pilot=COORDINATION):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        choices=(*pilot.suites, *(name for name, _ in pilot.suite_groups), "all"),
        default=pilot.default_suite,
    )
    if pilot.model_configs:
        parser.add_argument(
            "--model",
            choices=("all", *(m for m, _ in pilot.model_configs)),
            default="all",
            help="Run each selected model separately",
        )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        default=True,
        help="Select models/tasks in MindTrial (default)",
    )
    mode.add_argument(
        "--non-interactive",
        dest="interactive",
        action="store_false",
        help="Run configured models/tasks without prompts; require complete results",
    )
    parser.add_argument("--preflight-only", action="store_true", help="Qualify without model calls")
    parser.add_argument(
        "--task-id",
        action="append",
        default=[],
        help="Select one exact task name or unique row suffix (repeat this flag for several rows)",
    )
    parser.add_argument(
        "--repeat",
        type=positive_integer,
        default=1,
        help="Repeat the selected jobs in separate result folders, preserving the world seed",
    )
    parser.add_argument(
        "--skip-build", action="store_true", help="Verify and qualify an existing image"
    )
    args = parser.parse_args(argv)
    package = Path(package_dir or __file__).resolve()
    if package_dir is None:
        package = package.parent
    invoked = timestamp()
    try:
        if sys.version_info < (3, 12):  # noqa: UP036 -- standalone launcher runs outside the 3.14 image
            raise RunnerError("Python 3.12 or newer is required; set PYTHON to its executable.")
        release = load_release(package, pilot)
        suites = selected_suites(args.suite, pilot)
        # Reject selection mistakes before a build or provider request. Qualification
        # still covers the full release; repeat selection on its verified output.
        packaged_tasks = {
            suite: read_json(package / f"nexus-{pilot.name}-{suite}-tasks.yaml") for suite in suites
        }
        chosen = select_task_ids(packaged_tasks, suites, args.task_id)
        suites = tuple(chosen)
        if pilot.model_configs:
            model_configs = dict(pilot.model_configs)
            config_names = (
                set(model_configs.values()) if args.model == "all" else {model_configs[args.model]}
            )
            jobs = [
                (suite, name) for name in pilot.configs if name in config_names for suite in suites
            ]
        else:
            jobs = [(suite, config_for_suite(suite, pilot)) for suite in suites]
            config_names = {name for _, name in jobs}
        configs = {
            name: load_config(package, release, name)
            for name in pilot.configs
            if name in config_names
        }
        repository = Path(os.environ.get("NEXUS_REPO", str(Path.home() / "Go-Projects/NEXUS")))
        mindtrial = Path(os.environ.get("MINDTRIAL_DIR", str(Path.home() / "MindTrial")))
        repository, mindtrial = repository.expanduser().resolve(), mindtrial.expanduser().resolve()
        if not args.preflight_only:
            require_credentials(configs)
            binary = mindtrial / "mindtrial"
            if not binary.is_file() or not os.access(binary, os.X_OK):
                raise RunnerError(f"No executable mindtrial in MINDTRIAL_DIR: {mindtrial}")
        if not args.skip_build:
            print("Building the exact release commit from a temporary git archive...", flush=True)
            build_image(repository, release)
        image = inspect_image(release)
        print(
            "Qualifying the installed runtime and checking task exports; no model calls...",
            flush=True,
        )
        preflight = qualify(package, release, image, "repeat" in suites, pilot=pilot)
        if args.preflight_only:
            directory = result_directory(package, args.suite + "-preflight")
            write_json(directory / "preflight.json", preflight)
            write_json(directory / "release.json", release)
            write_json(
                directory / "manifest.json",
                {
                    "version": f"{pilot.name}-run-v1",
                    "status": "preflight-passed",
                    "suite": args.suite,
                    "interactive": args.interactive,
                    "requested_task_ids": args.task_id,
                    "repetitions": args.repeat,
                    "selected_task_names": {
                        suite: [task["name"] for task in value["task-config"]["tasks"]]
                        for suite, value in chosen.items()
                    },
                    "invocation_timestamp": invoked,
                    "finished_at": timestamp(),
                    "image": image,
                    "source_commit": release["source_commit"],
                    "runtime_source_sha256": preflight["runtime_source_sha256"],
                    "input_configs": {
                        name: {
                            "sha256": sha256(raw),
                            "contract_sha256": config_contract_sha256(config),
                            "matches_release": sha256(raw) == release["files_sha256"][name],
                            **(
                                {
                                    "tool_contract": tool_contract(
                                        config, pilot.tool_contract_version
                                    )
                                }
                                if pilot.tool_contract_version
                                else {}
                            ),
                        }
                        for name, (config, raw) in configs.items()
                    },
                    "command": None,
                },
            )
            print(f"Preflight passed; no model calls. Report: {directory}", flush=True)
            return 0
        for repetition in range(1, args.repeat + 1):
            for suite, config_name in jobs:
                config, config_raw = configs[config_name]
                admission = None
                if pilot.control_suite and suite not in (pilot.control_suite, *pilot.ungated_suites):
                    admission = control_admission(
                        package, release, config_name, config_raw, mindtrial / "mindtrial",
                        preflight["tasks"][pilot.control_suite], pilot=pilot,
                    )
                code = run_suite(
                    package,
                    suite,
                    config,
                    config_raw,
                    release,
                    image,
                    preflight,
                    mindtrial,
                    invoked,
                    pilot=pilot,
                    input_config_file=config_name,
                    interactive=args.interactive,
                    task_ids=(
                        [task["name"] for task in chosen[suite]["task-config"]["tasks"]]
                        if args.task_id
                        else ()
                    ),
                    repetition=repetition,
                    repetitions=args.repeat,
                    admission=admission,
                )
                if code:
                    return code
        return 0
    except (RunnerError, OSError, tarfile.TarError) as exc:
        # Do not print raw subprocess output, configuration values or environment.
        message = str(exc) if isinstance(exc, RunnerError) else type(exc).__name__
        print(f"Pilot blocked: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
