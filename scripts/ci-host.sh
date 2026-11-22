#!/usr/bin/env bash
# Non-pytest checks: ownership and preserved commands are documented in docs/development/testing.md.
set -euo pipefail
: "${NEXUS_CI_TEMP:?Run through make ci GROUP=...}"
case "${1:?Expected a CI group}" in
  quality)
    # Lock, partition, lint and clean installations
    uv lock --check
    uv run --frozen --all-extras python scripts/ci.py partition --output ci-results/quality/partition.json
    make check
    bash scripts/check_workflows.sh
    make package
    ;;
  core)
    ;;
  scientific)
    # Check immutable dynamics reference
    uv run --frozen --all-extras python scripts/compile_dynamics_reference.py
    # Check immutable transfer reference and pilot
    uv run --frozen --all-extras python scripts/compile_transfer_observations.py
    uv run --frozen --all-extras python scripts/compile_transfer_reference.py
    uv run --frozen --all-extras python scripts/preflight_transfer.py --output "$NEXUS_CI_TEMP/nexus-transfer-preflight.json"
    uv run --frozen --all-extras python scripts/preflight_transfer.py --matrix docs/astra-diagnostic-matrix.json --output "$NEXUS_CI_TEMP/nexus-astra-preflight.json"
    # History PoC proof and matrix
    uv run --frozen --all-extras python scripts/history_oracle.py --output "$NEXUS_CI_TEMP/history-proof.json"
    uv run --frozen --all-extras python scripts/preflight_history.py --output "$NEXUS_CI_TEMP/history-preflight.json"
    # Staged repair independent proof and matrix
    uv run --frozen --all-extras python scripts/staged_repair_oracle.py --output "$NEXUS_CI_TEMP/staged-proof.json"
    uv run --frozen --all-extras python scripts/preflight_staged_repair.py --output "$NEXUS_CI_TEMP/staged-preflight.json"
    # Joint assembly independent proof and qualified matrix
    uv run --frozen --all-extras python scripts/joint_assembly_oracle.py --output "$NEXUS_CI_TEMP/assembly-proof.json"
    uv run --frozen --all-extras python scripts/preflight_joint_assembly.py --output "$NEXUS_CI_TEMP/assembly-preflight.json"
    # Discovery PoC independent proofs and paired matrix
    uv run --frozen --all-extras python scripts/discovery_oracle.py --output "$NEXUS_CI_TEMP/discovery-proof.json"
    uv run --frozen --all-extras python scripts/preflight_discovery.py --output "$NEXUS_CI_TEMP/discovery-preflight.json"
    # Coupled memory independent proof and paired pilot
    uv run --frozen --all-extras python scripts/preflight_coupled_memory.py --output "$NEXUS_CI_TEMP/coupled-preflight.json" --proof-output "$NEXUS_CI_TEMP/coupled-proof.json"
    # Stateful trajectory qualification and paired matrix
    uv run --frozen --all-extras python scripts/preflight_stateful.py --output "$NEXUS_CI_TEMP/stateful-preflight.json"
    # Model revision independent proof and paired matrix
    uv run --frozen --all-extras python scripts/preflight_revision.py --output "$NEXUS_CI_TEMP/revision-preflight.json"
    ;;
  planning)
    # Planning/resource independent costs and matched pilot
    uv run --frozen --all-extras python scripts/preflight_planning.py --output "$NEXUS_CI_TEMP/planning-resource-preflight.json"
    # Coordination independent costs and paired controls
    uv run --frozen --all-extras python scripts/preflight_coordination.py --output "$NEXUS_CI_TEMP/coordination-preflight.json" --tasks-output "$NEXUS_CI_TEMP/coordination-tasks"
    # Disclosed interference independent costs and subgoal regression
    uv run --frozen --all-extras python scripts/preflight_interference.py --output "$NEXUS_CI_TEMP/interference-preflight.json" --tasks-output "$NEXUS_CI_TEMP/interference-tasks"
    # Two-model interference comparison structural qualification
    uv run --frozen --all-extras python scripts/preflight_interference_comparison.py --output "$NEXUS_CI_TEMP/interference-comparison-preflight.json" --tasks-output "$NEXUS_CI_TEMP/interference-comparison-tasks"
    ;;
  interfaces)
    # CLI smoke test
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-smoke" --seed 17 --discovery-level 2 \
      --planning-level 3 --resource-pressure 2
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-smoke/private.json" "$NEXUS_CI_TEMP/nexus-smoke/run.jsonl"
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-t3-smoke" --seed 17 --discovery-level 2 \
      --planning-level 3 --resource-pressure 2 --theory-level 3
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-t3-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-t3-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-t3-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-t3-smoke/private.json" "$NEXUS_CI_TEMP/nexus-t3-smoke/run.jsonl"
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-science-smoke" --axis-version 2 --seed 17 \
      --discovery-level 5 --theory-level 3 --planning-level 1 --resource-pressure 1
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-science-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-science-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-science-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-science-smoke/private.json" "$NEXUS_CI_TEMP/nexus-science-smoke/run.jsonl"
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-network-smoke" --axis-version 2 --seed 17 \
      --science-family coupled-network-v1 --discovery-level 5 --theory-level 3 \
      --planning-level 1 --resource-pressure 1
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-network-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-network-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-network-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-network-smoke/private.json" "$NEXUS_CI_TEMP/nexus-network-smoke/run.jsonl"
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-resonant-smoke" --axis-version 2 --seed 17 \
      --science-family resonant-network-v1 --discovery-level 5 --theory-level 3 \
      --planning-level 1 --resource-pressure 1
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-resonant-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-resonant-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-resonant-smoke/private.json" "$NEXUS_CI_TEMP/nexus-resonant-smoke/run.jsonl"

    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-causal-smoke" --axis-version 2 --seed 17 \
      --science-family causal-mechanisms-v1 --discovery-level 5 --theory-level 3 \
      --planning-level 1 --resource-pressure 1
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-causal-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-causal-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-causal-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-causal-smoke/private.json" "$NEXUS_CI_TEMP/nexus-causal-smoke/run.jsonl"
    uv run --frozen --all-extras nexus generate "$NEXUS_CI_TEMP/nexus-repair-smoke" --axis-version 2 --seed 17 \
      --science-family coupled-repair-v1 --discovery-level 5 --theory-level 3 \
      --planning-level 1 --resource-pressure 1
    uv run --frozen --all-extras nexus qualify "$NEXUS_CI_TEMP/nexus-repair-smoke/private.json"
    uv run --frozen --all-extras nexus solve "$NEXUS_CI_TEMP/nexus-repair-smoke/private.json" --trace-out "$NEXUS_CI_TEMP/nexus-repair-smoke/run.jsonl"
    uv run --frozen --all-extras nexus replay "$NEXUS_CI_TEMP/nexus-repair-smoke/private.json" "$NEXUS_CI_TEMP/nexus-repair-smoke/run.jsonl"
    ;;
  evaluation)
    # Cross-axis current-source qualification and task export
    uv run --frozen --all-extras python scripts/preflight_cross_axis.py --output "$NEXUS_CI_TEMP/cross-axis-preflight.json" --tasks-output "$NEXUS_CI_TEMP/cross-axis-tasks"
    # Fresh-world mechanical qualification
    uv run --frozen --all-extras python scripts/fresh_worlds.py --output "$NEXUS_CI_TEMP/fresh-world-preflight.json" --tasks-output "$NEXUS_CI_TEMP/fresh-world-tasks"
    ;;
  *) echo "Unknown host group: $1" >&2; exit 2 ;;
esac
