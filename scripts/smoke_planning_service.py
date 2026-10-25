"""Operator-only real process/HTTP/CLI/receipt check; no model or provider calls.

Read the actual MindTrial configuration and task inputs. A subprocess stands in
for the task-owned service; short-lived CLI processes stand in for tool and
validator containers. Docker CI additionally runs this inside the built image.
This does not execute MindTrial's Docker orchestration or a model provider.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.error import HTTPError
from urllib.request import urlopen

from nexus.evaluation.artifacts import atomic_json
from nexus.models.observation import Observation
from nexus.ontology.planning.policy import public_policy
from nexus.protocol.session import ActionResponse, SessionStatus

CLI = str(Path(sys.executable).parent / "nexus")


def cli(command, env):
    result = subprocess.run([CLI, *command], env=env, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f"NEXUS CLI failed: {result.stderr[-2000:]}")
    return result


def run_case(config, task, folder, *, forged=False):
    service, tool, validator = (config[key][0] for key in ("services", "tools", "validators"))
    inputs = task["tool-selector"]["service-inputs"][service["name"]]
    env = {k: v for k, v in os.environ.items() if not k.startswith("NEXUS_")}
    env.update(service["env"])
    env.update(
        {
            service["input-env"][key]: str(value).lower() if isinstance(value, bool) else str(value)
            for key, value in inputs.items()
        }
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env.update(NEXUS_HOST="127.0.0.1", NEXUS_PORT=str(port))
    url = f"http://127.0.0.1:{port}"
    client_env = {**env, "NEXUS_URL": url}
    request_file, candidate_file = folder / "request.json", folder / "candidate.txt"
    calls = 0

    def request(payload):
        nonlocal calls
        calls += 1
        request_file.write_text(json.dumps(payload))
        command = [
            str(request_file) if value == tool["parameter-files"]["request"] else value
            for value in tool["command"]
        ]
        result = json.loads(cli(command, client_env).stdout)
        if not result.get("victory_code") and not result.get("performance"):
            encoded = json.dumps(result)
            for field in (
                "construction_seed",
                "investigation_truth",
                "verifier_secret",
                "reference_action_upper",
            ):
                if f'"{field}"' in encoded:
                    raise ValueError(f"private field leaked through player request: {field}")
        return result

    def validate(candidate):
        candidate_file.write_text(candidate)
        command = [
            str(candidate_file) if value == validator["template-files"][0]["path"] else value
            for value in validator["command"]
        ]
        result = cli(command, client_env)
        if "NEXUS terminal performance:" not in result.stderr:
            raise ValueError("validator omitted terminal telemetry")
        return json.loads(result.stdout)

    class Player:
        def status(self):
            return SessionStatus.model_validate(request({"operation": "status"}))

        def observe(self):
            return Observation.model_validate(request({"operation": "observe"}))

        def act(self, expected_turn, action):
            response = request({"operation": "action", "action": action.model_dump(mode="json")})
            if not response.get("victory_code") and response.get("performance") is not None:
                raise ValueError("public reference unexpectedly terminated or exposed diagnostics")
            return ActionResponse.model_validate(response)

    log_path = folder / "service.log"
    with log_path.open("w") as log:
        process = subprocess.Popen([CLI, *service["command"]], env=env, stdout=log, stderr=log)
        try:
            deadline = monotonic() + 120
            while True:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"service exited during startup: {log_path.read_text()[-2000:]}"
                    )
                try:
                    with urlopen(url + "/health", timeout=1) as response:
                        if json.load(response).get("status") == "ok":
                            break
                except OSError:
                    pass
                if monotonic() >= deadline:
                    raise TimeoutError("NEXUS service did not become healthy")
                sleep(0.1)
            cli(service["healthcheck"][1:], client_env)
            for hidden_path in ("/sessions", "/operator-diagnostics"):
                try:
                    urlopen(url + hidden_path, timeout=5).close()
                except HTTPError as exc:
                    if exc.code != 404:
                        raise
                else:
                    raise ValueError(f"unexpected endpoint available: {hidden_path}")
            if forged:
                if validate("NX-FORGED")["correct"]:
                    raise ValueError("forged receipt accepted before playing")
                if request({"operation": "status"})["status"] != "failed":
                    raise ValueError("failed validation did not finalize the attempt")
                if request({"operation": "action", "action": {"type": "wait"}})["ok"]:
                    raise ValueError("finalized attempt continued")
                outcome = {"case": task["name"], "forged_receipt_rejected": True}
            else:
                manifest = request({"operation": "manifest"})
                request({"operation": "observe"})
                evidence = {
                    name: request({"operation": "evidence", "filename": name})["content"]
                    for name in manifest["evidence_files"]
                }
                result = public_policy(Player(), evidence)
                if not result.victory_code or not validate(result.victory_code)["correct"]:
                    raise ValueError("public policy receipt was not accepted")
                if validate(result.victory_code + "-WRONG")["correct"]:
                    raise ValueError("wrong receipt accepted after winning")
                if result.performance.decision_diagnostics.escape_classification != "supported_win":
                    raise ValueError("reference win lacked public support")
                outcome = {
                    "case": task["name"],
                    "actions": result.current_turn,
                    "tool_requests": calls,
                    "receipt_accepted": True,
                    "wrong_receipt_rejected": True,
                    "supported_win": True,
                }
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    if "NEXUS operator summary:" not in log_path.read_text():
        raise ValueError("service shutdown omitted operator summary")
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("examples/mindtrial/nexus-planning-resource-config.yaml"),
    )
    parser.add_argument(
        "--tasks", type=Path, default=Path("examples/mindtrial/nexus-planning-resource-tasks.yaml")
    )
    parser.add_argument(
        "--rows", default="04,07", help="Stable row IDs, comma-separated; all for 16 cells"
    )
    parser.add_argument("--output", type=Path, default=Path("/tmp/planning-service-smoke.json"))
    args = parser.parse_args()
    report = {
        "version": "planning-service-smoke-v1",
        "status": "running",
        "cases": [],
        "scope": "Actual NEXUS process, HTTP, stateless CLI and receipt validator; no MindTrial/provider execution",
    }
    atomic_json(args.output, report)
    try:
        config = json.loads(args.config.read_text())["config"]
        task_config = json.loads(args.tasks.read_text())["task-config"]
        requested = {r.strip() for r in args.rows.split(",")}
        selected = [
            t
            for t in task_config["tasks"]
            if args.rows == "all" or t["name"].rsplit("-", 1)[1] in requested
        ]
        if not selected or (args.rows != "all" and len(selected) != len(requested)):
            raise ValueError("unknown or duplicate smoke row selection")
        with TemporaryDirectory(prefix="nexus-pr-smoke-") as directory:
            for task in selected:
                outcome = run_case(config, task, Path(directory))
                if outcome["tool_requests"] > task_config["tool-selector"]["tools"][0]["max-calls"]:
                    raise ValueError("reference exceeds harness tool allowance")
                report["cases"].append(outcome)
                atomic_json(args.output, report)
            report["negative_control"] = run_case(config, selected[0], Path(directory), forged=True)
        report["status"] = "passed"
        atomic_json(args.output, report)
        print(json.dumps(report))
    except Exception as exc:
        report.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
        atomic_json(args.output, report)
        raise


if __name__ == "__main__":
    main()
