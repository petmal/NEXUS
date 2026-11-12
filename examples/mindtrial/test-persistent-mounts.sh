#!/usr/bin/env bash
# Exercise the locally built NEXUS image, then one real MindTrial v0.26+ row.
set -euo pipefail
umask 077
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo=${NEXUS_REPO:-"$HOME/Go-Projects/NEXUS"}
mt_dir=${MINDTRIAL_DIR:-"$HOME/MindTrial"}
base=${OUTPUT_ROOT:-"$HOME/Downloads"}
mode=${1:---live}
case "$mode" in
  --preflight-only|--live) ;;
  *) echo "Usage: bash $0 [--preflight-only|--live]" >&2; exit 2 ;;
esac
mkdir -p -- "$base"
base=$(cd -- "$base" && pwd -P)
out=$(mktemp -d "$base/nexus-mount-smoke.XXXXXXXX")
printf 'Results: %s\n' "$out"
rev=$(git -C "$repo" rev-parse HEAD)
printf '%s\n' "$rev" > "$out/nexus-revision.txt"
if [[ $mode == --live ]]; then
  mt_dir=$(cd -- "$mt_dir" && pwd -P)
  mt="$mt_dir/mindtrial"
  "$mt" version | tee "$out/mindtrial-version.txt"
  python3 - "$out/mindtrial-version.txt" <<'PY'
import re, sys
from pathlib import Path
version = Path(sys.argv[1]).read_text().strip()
m = re.match(r"MindTrial v(\d+)\.(\d+)\.(\d+)", version)
if m and tuple(map(int, m.groups())) < (0, 26, 0):
    sys.exit("MindTrial v0.26.0 or newer is required.")
if not m:
    print("Unversioned local binary: make sure it was built from v0.26.0 or newer.", file=sys.stderr)
PY
fi
# Build committed source only; an unpublished NEXUS checkout is sufficient.
if [[ -n ${NEXUS_SMOKE_IMAGE:-} ]]; then
  image=$(docker image inspect -f '{{.Id}}' "$NEXUS_SMOKE_IMAGE")
  label=$(docker image inspect -f '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$image")
  [[ $label == "$rev" ]] || { echo "Image revision differs from checkout HEAD." >&2; exit 1; }
  printf '%s\n' "$image" > "$out/image-id"
else
  git -C "$repo" archive "$rev" | docker build --build-arg "VCS_REF=$rev" --iidfile "$out/image-id" -
  image=$(<"$out/image-id")
fi
opts=()
if [[ ${TEXT_OUTPUT:-0} == 1 ]]; then opts+=(--text-output); fi
python3 "$here/first_run.py" "$out/run" --provider "${PROVIDER:-openai}" \
  --model "${MODEL:-gpt-6-luna}" --image "$image" "${opts[@]}"
audits="$out/run/private-audits"
# :z labels ONLY our newly created, dedicated directory for sharing on SELinux.
# MindTrial itself never relabels operator-owned directories.
cid=''
cleanup() { if [[ -n $cid ]]; then docker rm -f "$cid" >/dev/null || :; fi; }
trap cleanup EXIT
cid=$(docker run -d --network none -v "$audits:/nexus-audits:z" \
  -e NEXUS_AUDIT_DIR=/nexus-audits/preflight "$image" serve-session --seed 17)
ready=0
for ((i=0; i<60; i++)); do
  if docker exec "$cid" nexus health >/dev/null 2>&1; then ready=1; break; fi
  if [[ $(docker inspect -f '{{.State.Running}}' "$cid") != true ]]; then break; fi
  sleep 1
done
if (( !ready )); then docker logs "$cid" >&2; exit 1; fi
docker exec -i "$cid" nexus request --request-file /dev/stdin <<< '{"operation":"observe"}' >/dev/null
docker stop -t 10 "$cid" >/dev/null
docker rm "$cid" >/dev/null
cid=''
docker run --rm --network none -v "$audits:/nexus-audits:ro" "$image" \
  verify-audit /nexus-audits/preflight --json > "$out/preflight.json"
python3 - "$out/preflight.json" <<'PY'
import json, sys
with open(sys.argv[1]) as f: r = json.load(f)
if not (r["world_status"] == "active" and r["trace_replay_verified"] and r["public_capture_complete"]):
    sys.exit("Preflight did not preserve a verified, unfinished session.")
print("Docker preflight passed: the stopped container's unfinished session replays from the mount.")
PY
if [[ $mode == --preflight-only ]]; then exit 0; fi
rc=0
(cd -- "$mt_dir" && "$mt" -config="$out/run/config.yaml" -tasks="$out/run/tasks.yaml" \
  --debug --interactive=false --json --evaluation-seed=nexus-mount-smoke-v1 run) || rc=$?
# A harness error or failed answer must not prevent inspection of retained attempts.
audit_rc=0
python3 "$here/verify_mount_smoke.py" "$out/run" "$image" || audit_rc=$?
if (( rc )); then echo "MindTrial exit $rc; see $out" >&2; exit "$rc"; fi
exit "$audit_rc"
