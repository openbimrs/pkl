#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PKL_BIN="${PKL_BIN:-pkl}"
PACKAGE="packages/openbim.loin"
CONSUMER="examples/consumer"

"$PKL_BIN" --version
mapfile -d '' -t pkl_sources < <(git ls-files -z '*.pkl' '**/PklProject')
((${#pkl_sources[@]} > 0))
"$PKL_BIN" format --diff-name-only "${pkl_sources[@]}"
"$PKL_BIN" project resolve "$PACKAGE"
"$PKL_BIN" project resolve "$CONSUMER"
"$PKL_BIN" test "$PACKAGE/tests/loin.pkl"

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

"$PKL_BIN" eval \
  --format pcf \
  --output-path "$scratch/basic.pcf" \
  "$PACKAGE/examples/basic.pkl"
"$PKL_BIN" eval \
  --project-dir "$CONSUMER" \
  --format pcf \
  --output-path "$scratch/consumer.pcf" \
  "$CONSUMER/application.pkl"
"$PKL_BIN" project package \
  --skip-publish-check \
  --output-path "$scratch/package" \
  "$PACKAGE"

test -s "$scratch/basic.pcf"
test -s "$scratch/consumer.pcf"
for artifact in \
  openbim.loin@0.1.0 \
  openbim.loin@0.1.0.sha256 \
  openbim.loin@0.1.0.zip \
  openbim.loin@0.1.0.zip.sha256
do
  test -s "$scratch/package/$artifact"
done

printf 'openbim Pkl gate: ok\n'
