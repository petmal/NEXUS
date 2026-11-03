#!/usr/bin/env bash
# Continue after the ten recorded Astra attempts; stop on any further blocker.
set -euo pipefail
fix_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
package_dir="${1:-${HOME}/Downloads/NEXUS-fresh-world-test-run-2026-11-03}"
if (( $# > 1 )); then
    echo "Usage: bash resume.sh [original-package-directory]" >&2
    exit 2
fi
"${PYTHON:-python3}" "${fix_dir}/apply.py" --package "${package_dir}"
bash "${package_dir}/run.sh" --model astra --suite challenges --non-interactive --skip-build
for model in luna flash grok; do
    bash "${package_dir}/run.sh" --model "${model}" --suite fresh --non-interactive --skip-build
done
