#!/usr/bin/env bash
# Build the seven tool images from containers/<tool>/ and push them to a registry
# (default: ghcr.io/labiomics/metalncrna-<tool>:<version>).
#
# With --update-manifest, rewrites the `ref` lines of src/metalncrna/manifest.toml to the pushed
# images pinned by digest.
#
# Needs docker with registry credentials. For GHCR the gh token needs the write:packages scope:
#   gh auth refresh -h github.com -s write:packages,read:packages
set -euo pipefail

NS=${NS:-ghcr.io/labiomics}
PREFIX=${PREFIX:-metalncrna-}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
MANIFEST=$ROOT/src/metalncrna/manifest.toml
UPDATE=0
[[ ${1:-} == --update-manifest ]] && UPDATE=1

# tool -> version tag (upstream version of the tool)
declare -A VERSION=(
  [cnci]="2-745e2d1" [cppred]="2018.05.17" [lgc]="1.0"
  [cpat]="3.0.5" [cpc2]="1.0.1" [plek]="1.2" [rnasamba]="0.2.5"
)
TOOLS=(cnci cppred lgc cpat cpc2 plek rnasamba)

if [[ $NS == ghcr.io/* ]] && command -v gh >/dev/null; then
  gh auth token | docker login ghcr.io -u "$(gh api user --jq .login)" --password-stdin >/dev/null
fi

declare -A REF
for tool in "${TOOLS[@]}"; do
  dst="$NS/$PREFIX$tool:${VERSION[$tool]}"
  echo "== $tool -> $dst" >&2
  docker build -q -t "$dst" "$ROOT/containers/$tool" >/dev/null
  # GHCR sometimes denies the first push while it creates a new package; retry.
  for attempt in 1 2 3 4 5; do
    docker push -q "$dst" >/dev/null && break
    (( attempt == 5 )) && { echo "push failed: $dst" >&2; exit 1; }
    sleep $(( attempt * 5 ))
  done
  digest=$(docker buildx imagetools inspect "$dst" --format '{{json .Manifest}}' \
           | python3 -c 'import json,sys; print(json.load(sys.stdin)["digest"])')
  REF[$tool]="$dst@$digest"
  echo "   ${REF[$tool]}" >&2
done

if (( UPDATE )); then
  python3 - "$MANIFEST" "$(for t in "${TOOLS[@]}"; do echo "$t=${REF[$t]}"; done)" <<'EOF'
import re, sys
path, pairs = sys.argv[1], dict(l.split("=", 1) for l in sys.argv[2].splitlines())
text = open(path).read()
for tool, ref in pairs.items():
    text, n = re.subn(rf'(\[images\.{tool}\]\nref = )"[^"]*"', rf'\1"{ref}"', text)
    assert n == 1, tool
open(path, "w").write(text)
print(f"updated {path}", file=sys.stderr)
EOF
fi

for tool in "${TOOLS[@]}"; do printf '%-9s %s\n' "$tool" "${REF[$tool]}"; done
