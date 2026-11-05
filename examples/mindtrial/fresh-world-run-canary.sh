#!/usr/bin/env bash
# Six selected attempts on one model; the shared launcher owns all admission gates.
set -euo pipefail
usage() {
    cat <<'TEXT'
Usage: bash run-canary.sh MODEL [--preflight-only] [--skip-build]

MODEL is exactly one of: astra, luna, flash, grok.
Runs four matching controls (F01/F03/F05/F08), then F11/F12 unattended.
This makes paid model calls unless --preflight-only is set.
Preflight checks the image and all qualified fixtures without model calls or keys.
Use --skip-build only after this package's image has been built.
TEXT
}
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi
case "${1:-}" in
    astra|luna|flash|grok) model="$1"; shift ;;
    *) usage >&2; exit 2 ;;
esac
preflight=false
build_args=()
for arg in "$@"; do
    case "$arg" in
        --preflight-only) preflight=true ;;
        --skip-build) build_args=(--skip-build) ;;
        *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
    esac
done
package_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
runner="${package_dir}/run.sh"
if [[ ! -f "$runner" ]]; then
    runner="${package_dir}/fresh-world-run.sh"
fi
if [[ "$preflight" == true ]]; then
    exec bash "$runner" --model "$model" --suite fresh --preflight-only "${build_args[@]}"
fi
bash "$runner" --model "$model" --suite controls --non-interactive "${build_args[@]}"
bash "$runner" --model "$model" --suite pr-a --task-id F11 --task-id F12 \
    --non-interactive --skip-build
