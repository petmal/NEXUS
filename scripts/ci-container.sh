#!/usr/bin/env bash
# Installed-service coverage; never calls a provider or starts MindTrial.
set -euo pipefail
: "${NEXUS_CI_TEMP:?Run through make ci GROUP=container-...}"
case "${1:-}" in scientific|planning|panels) ;; *) echo "Unknown container group" >&2; exit 2 ;; esac
revision=$(git rev-parse HEAD)
docker build --build-arg VCS_REF="$revision" -t nexus-ci -t nexus:planning-resource-v1 -t nexus:coordination-v1 -t nexus:interference-v1 -t nexus:interference-comparison-v1 -t nexus:cross-axis-v1 -t nexus:capability-smoke-v1 -t nexus:fresh-world-v1 .
test "$(docker image inspect nexus-ci --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}')" = "$revision"
case "$1" in
  scientific)
    # Legacy and scientific image contracts
    docker run --rm --entrypoint python nexus-ci --version
    docker run --rm --entrypoint python nexus-ci scripts/preflight_repair.py
    docker run --rm --entrypoint python nexus-ci scripts/preflight_matrix.py --output /tmp/matrix-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_structural.py --output /tmp/structural-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_budget.py --output /tmp/budget-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_transfer.py --output /tmp/transfer-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_transfer.py --matrix docs/astra-diagnostic-matrix.json --output /tmp/astra-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_history.py --output /tmp/history-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_staged_repair.py --output /tmp/staged-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_joint_assembly.py --output /tmp/assembly-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_discovery.py --output /tmp/discovery-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_coupled_memory.py --output /tmp/coupled-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_stateful.py --output /tmp/stateful-preflight.json
    docker run --rm --entrypoint python nexus-ci scripts/preflight_revision.py --output /tmp/revision-preflight.json
    docker run --rm nexus-ci --help
    docker run --rm nexus-ci generate /tmp/nexus-t3 --seed 17 \
      --discovery-level 2 --planning-level 0 --theory-level 3
    docker run --rm nexus-ci generate /tmp/nexus-science --axis-version 2 --seed 17 \
      --discovery-level 5 --planning-level 0 --theory-level 3 --resource-pressure 0
    docker run --rm -e NEXUS_SCIENCE_FAMILY=coupled-network-v1 nexus-ci generate \
      /tmp/nexus-network --axis-version 2 --seed 17 --discovery-level 5 \
      --planning-level 1 --theory-level 3 --resource-pressure 1
    docker run --rm -e NEXUS_SCIENCE_FAMILY=resonant-network-v1 nexus-ci generate \
      /tmp/nexus-resonant --axis-version 2 --seed 17 --discovery-level 5 \
      --planning-level 1 --theory-level 3 --resource-pressure 1
    docker run --rm -e NEXUS_SCIENCE_FAMILY=causal-mechanisms-v1 nexus-ci generate \
      /tmp/nexus-causal --axis-version 2 --seed 17 --discovery-level 5 \
      --planning-level 1 --theory-level 3 --resource-pressure 1
    docker run --rm -e NEXUS_SCIENCE_FAMILY=coupled-repair-v1 nexus-ci generate \
      /tmp/nexus-repair --axis-version 2 --seed 17 --discovery-level 5 \
      --planning-level 1 --theory-level 3 --resource-pressure 1
    ;;
  planning)
    # Qualify all 16 cases inside the image
    docker run --rm --entrypoint python nexus:planning-resource-v1 scripts/preflight_planning.py
    # Qualify all 40 coordination cases inside the image
    docker run --rm --entrypoint python nexus:coordination-v1 scripts/preflight_coordination.py
    # Qualify all 32 interference cases inside the image
    docker run --rm --entrypoint python nexus:interference-v1 scripts/preflight_interference.py
    # Qualify all 32 comparison rows and structural metrics inside the image
    docker run --rm --entrypoint python nexus:interference-comparison-v1 scripts/preflight_interference_comparison.py
    # Exercise real service, tool client, validator and shutdown telemetry
    docker run --rm --entrypoint python \
      --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
      nexus:planning-resource-v1 scripts/smoke_planning_service.py \
      --config /run-config/nexus-planning-resource-config.yaml \
      --tasks /run-config/nexus-planning-resource-tasks.yaml --rows all
    # Exercise coordination core and spatial services and receipts
    for suite in core spatial slack; do
      docker run --rm --entrypoint python \
        --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
        nexus:coordination-v1 scripts/smoke_planning_service.py \
        --config /run-config/nexus-coordination-config.yaml \
        --tasks "/run-config/nexus-coordination-$suite-tasks.yaml" --rows all
    done
    # Exercise all comparison services and receipts at both budgets
    for suite in core slack; do
      docker run --rm --entrypoint python \
        --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
        nexus:interference-comparison-v1 scripts/smoke_planning_service.py \
        --config /run-config/nexus-interference-comparison-config.yaml \
        --tasks "/run-config/nexus-interference-comparison-$suite-tasks.yaml" --rows all
    done
    # Preserve the original interference profile service contract
    docker run --rm --entrypoint python \
      --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
      nexus:interference-v1 scripts/smoke_planning_service.py \
      --config /run-config/nexus-interference-config.yaml \
      --tasks /run-config/nexus-interference-core-tasks.yaml --rows 01
    ;;
  panels)
    # The mount smoke intentionally writes private files as the image's user.
    # Remove only this run's dedicated directories through that same image, so
    # host TemporaryDirectory cleanup also works on rootful/rootless Docker.
    cleanup_mount_smoke() {
      docker run --rm --network none \
        --mount "type=bind,source=$NEXUS_CI_TEMP,target=/ci-cleanup" \
        --entrypoint python nexus-ci -c \
        'from pathlib import Path; import shutil; [shutil.rmtree(p) for p in Path("/ci-cleanup").glob("nexus-mount-smoke.*")]'
    }
    trap cleanup_mount_smoke EXIT
    # Verify a private audit after removing the service container
    NEXUS_REPO="$PWD" OUTPUT_ROOT="$NEXUS_CI_TEMP" NEXUS_SMOKE_IMAGE=nexus:planning-resource-v1 bash examples/mindtrial/test-persistent-mounts.sh --preflight-only
    # Qualify all 56 cross-axis conditions inside the image
    docker run --rm --entrypoint python nexus:cross-axis-v1 scripts/preflight_cross_axis.py
    # Qualify all fresh-world contrasts inside the image
    docker run --rm --entrypoint python nexus:fresh-world-v1 scripts/fresh_worlds.py --output /tmp/fresh-preflight.json
    # Verify the packaged launcher against the actual image without model calls
    runtime_digest=$(docker run --rm --entrypoint python nexus:coordination-v1 -c 'from nexus.provenance import source_digest; print(source_digest())')
    python3 scripts/package_coordination.py --output-dir "$NEXUS_CI_TEMP/coordination-package" --runtime-source-sha256 "$runtime_digest"
    bash "$NEXUS_CI_TEMP/coordination-package/run.sh" --skip-build --preflight-only --suite all
    python3 scripts/package_interference.py --output-dir "$NEXUS_CI_TEMP/interference-package" --runtime-source-sha256 "$runtime_digest"
    bash "$NEXUS_CI_TEMP/interference-package/run.sh" --skip-build --preflight-only --suite all
    # The dated comparison release remains pinned to its original source/probe.
    # Its current mechanics/services and package unit tests remain checked;
    # cross-axis is the current release's full launcher integration gate.
    uv run --frozen --all-extras python scripts/package_cross_axis.py --output-dir "$NEXUS_CI_TEMP/cross-axis-package" --runtime-source-sha256 "$runtime_digest"
    bash "$NEXUS_CI_TEMP/cross-axis-package/run.sh" --skip-build --preflight-only --suite all
    uv run --frozen --all-extras python scripts/package_capability_smoke.py --output-dir "$NEXUS_CI_TEMP/capability-smoke-package" --runtime-source-sha256 "$runtime_digest"
    bash "$NEXUS_CI_TEMP/capability-smoke-package/run.sh" --skip-build --preflight-only --suite all
    uv run --frozen --all-extras python scripts/package_fresh_world.py --output-dir "$NEXUS_CI_TEMP/fresh-world-package" --runtime-source-sha256 "$runtime_digest"
    bash "$NEXUS_CI_TEMP/fresh-world-package/run.sh" --skip-build --preflight-only --suite all
    # Exercise every cross-axis condition through the family-neutral contract
    for suite in canary-core canary-slack rerun-core rerun-slack smoke-td smoke-pr; do
      case "$suite" in
        canary-*) config=canary ;;
        rerun-*) config=rerun ;;
        smoke-*) config=smoke ;;
      esac
      docker run --rm --entrypoint python \
        --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
        nexus:cross-axis-v1 scripts/smoke_planning_service.py \
        --config "/run-config/nexus-cross-axis-$config-config.yaml" \
        --tasks "/run-config/nexus-cross-axis-$suite-tasks.yaml" --rows all
    done
    # Exercise every fresh-world service and receipt
    for suite in controls td pr-a pr-b; do
      docker run --rm --entrypoint python \
        --mount "type=bind,source=$PWD/examples/mindtrial,target=/run-config,readonly" \
        nexus:fresh-world-v1 scripts/smoke_planning_service.py \
        --config /run-config/nexus-fresh-world-astra-config.yaml \
        --tasks "/run-config/nexus-fresh-world-$suite-tasks.yaml" --rows all
    done
    ;;
esac
