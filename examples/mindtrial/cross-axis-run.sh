#!/usr/bin/env bash
set -euo pipefail
package_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
runner="${package_dir}/runner.py"
if [[ ! -f "${runner}" ]]; then
    runner="${package_dir}/cross-axis-runner.py"
fi
exec "${PYTHON:-python3}" "${runner}" "$@"
