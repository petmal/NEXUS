#!/usr/bin/env bash
# One disclosed control at a lower request rate; no automatic repetition.
set -euo pipefail
package_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"${PYTHON:-python3}" - "$package_dir/nexus-capability-smoke-minimax-config.yaml" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
raw = path.read_bytes()
config = json.loads(raw)
providers = config['config']['providers']
if len(providers) != 1 or providers[0]['name'] != 'openrouter' or len(providers[0]['runs']) != 1:
    raise SystemExit('Expected one OpenRouter MiniMax run; configuration was not changed.')
run = providers[0]['runs'][0]
if run['model'] != 'minimax/minimax-m3':
    raise SystemExit('Expected the original MiniMax model; configuration was not changed.')
backup = path.with_name(path.name + '.before-rate-probe')
if not backup.exists():
    backup.write_bytes(raw)
run['max-requests-per-minute'] = 2
run['name'] = 'MiniMax M3 - rate probe (2 RPM, text output)'
path.write_text(json.dumps(config, indent=2) + '\n')
PY
bash "$package_dir/run.sh" --model minimax --suite controls --task-id S05 --non-interactive "$@"
