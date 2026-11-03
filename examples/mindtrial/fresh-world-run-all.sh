#!/usr/bin/env bash
# One contemporary Astra anchor, then the four-model fresh panel, unattended.
set -euo pipefail
package_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
runner="${package_dir}/run.sh"
if [[ ! -f "${runner}" ]]; then
    runner="${package_dir}/fresh-world-run.sh"
fi
if (( $# != 0 )); then
    echo "run-all.sh takes no arguments; use run.sh for selected models, tasks or reruns." >&2
    exit 2
fi
bash "${runner}" --model astra --suite anchor --non-interactive
bash "${runner}" --model all --suite fresh --non-interactive --skip-build
