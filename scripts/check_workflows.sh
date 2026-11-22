#!/usr/bin/env bash
# Pin the upstream release and archive digest; no pipe-to-shell installer.
set -euo pipefail
version=1.7.12
checksum=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
if [[ -n "${ACTIONLINT:-}" ]]; then
  "${ACTIONLINT}" -color
  exit
fi
if command -v actionlint >/dev/null 2>&1; then
  actionlint -color
  exit
fi
if [[ "$(uname -s)-$(uname -m)" != Linux-x86_64 ]]; then
  echo "Install actionlint $version or set ACTIONLINT to its executable." >&2
  exit 1
fi
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
archive="$temporary/actionlint.tar.gz"
curl --fail --silent --show-error --location --retry 3 \
  "https://github.com/rhysd/actionlint/releases/download/v$version/actionlint_${version}_linux_amd64.tar.gz" \
  --output "$archive"
printf '%s  %s\n' "$checksum" "$archive" | sha256sum --check
tar -xzf "$archive" -C "$temporary" actionlint
"$temporary/actionlint" -color
