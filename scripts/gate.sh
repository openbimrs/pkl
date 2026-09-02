#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PKL_BIN="${PKL_BIN:-pkl}"
LOIN_PACKAGE="packages/openbim.loin"
GEOMETRY_PACKAGE="packages/openbim.geometry"
IFC_PACKAGE="packages/openbim.ifc"
CONSUMER="examples/consumer"

"$PKL_BIN" --version
"$PKL_BIN" format --diff-name-only \
  packages \
  examples \
  "$LOIN_PACKAGE/PklProject" \
  "$GEOMETRY_PACKAGE/PklProject" \
  "$IFC_PACKAGE/PklProject" \
  examples/consumer/PklProject

"$PKL_BIN" project resolve "$LOIN_PACKAGE"
"$PKL_BIN" project resolve "$GEOMETRY_PACKAGE"
"$PKL_BIN" project resolve "$IFC_PACKAGE"
"$PKL_BIN" project resolve "$CONSUMER"
"$PKL_BIN" test "$LOIN_PACKAGE/tests/loin.pkl"
"$PKL_BIN" test "$GEOMETRY_PACKAGE/tests/geometry.pkl"
"$PKL_BIN" test "$IFC_PACKAGE/tests/ifc.pkl"
python3 scripts/check-ifc-modularity.py
python3 scripts/check-ifc-provenance.py
python3 scripts/mutation-gate.py

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

"$PKL_BIN" eval \
  --format pcf \
  --output-path "$scratch/loin-basic.pcf" \
  "$LOIN_PACKAGE/examples/basic.pkl"
"$PKL_BIN" eval \
  --format pcf \
  --output-path "$scratch/axiolid-manifest.pcf" \
  "$GEOMETRY_PACKAGE/examples/axiolid.pkl"
"$PKL_BIN" eval \
  --format pcf \
  --output-path "$scratch/analytic-brep-requirements.pcf" \
  "$GEOMETRY_PACKAGE/examples/requirements/analytic-brep.pkl"
"$PKL_BIN" eval \
  --format pcf \
  --output-path "$scratch/ifc-basic.pcf" \
  "$IFC_PACKAGE/examples/basic.pkl"
"$PKL_BIN" eval \
  --project-dir "$CONSUMER" \
  --format pcf \
  --output-path "$scratch/consumer.pcf" \
  "$CONSUMER/application.pkl"

for package in "$LOIN_PACKAGE" "$GEOMETRY_PACKAGE" "$IFC_PACKAGE"; do
  "$PKL_BIN" project package \
    --skip-publish-check \
    --output-path "$scratch/package" \
    "$package"
done

test -s "$scratch/loin-basic.pcf"
test -s "$scratch/axiolid-manifest.pcf"
test -s "$scratch/analytic-brep-requirements.pcf"
test -s "$scratch/ifc-basic.pcf"
test -s "$scratch/consumer.pcf"
for artifact in \
  openbim.loin@0.1.0 \
  openbim.loin@0.1.0.sha256 \
  openbim.loin@0.1.0.zip \
  openbim.loin@0.1.0.zip.sha256 \
  openbim.geometry@0.1.0 \
  openbim.geometry@0.1.0.sha256 \
  openbim.geometry@0.1.0.zip \
  openbim.geometry@0.1.0.zip.sha256 \
  openbim.ifc@0.3.0 \
  openbim.ifc@0.3.0.sha256 \
  openbim.ifc@0.3.0.zip \
  openbim.ifc@0.3.0.zip.sha256
do
  test -s "$scratch/package/$artifact"
done

printf 'openbim Pkl gate: ok\n'
