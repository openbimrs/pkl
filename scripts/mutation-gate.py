#!/usr/bin/env python3
"""Prove package tests reject representative semantic regressions."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKL = shutil.which("pkl")
if PKL is None:
    raise SystemExit("mutation gate failed: pkl is not on PATH")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(
            f"mutation gate failed: expected one marker in {path}, got {text.count(old)}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def run_test(candidate: Path, test: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PKL, "test", "--no-power-assertions", str(candidate / test)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def expect_rejected(label: str, package: str, test: str, mutation) -> None:
    with tempfile.TemporaryDirectory(prefix=f"openbim-{label}-mutation-") as directory:
        candidate = Path(directory) / package
        shutil.copytree(ROOT / "packages" / package, candidate)
        mutation(candidate)
        result = run_test(candidate, test)
        if result.returncode == 0:
            raise SystemExit(f"mutation gate failed: {label} regression survived")
        print(f"mutation rejected: {label}")


def expect_ifc_bundle_rejected() -> None:
    """One evaluation proves independent IFC facts kill all representative mutants.

    Parsing the generated template catalog dominates runtime. Mutating independent
    facts in one copy preserves per-fact evidence without paying that cost once per
    mutant.
    """
    with tempfile.TemporaryDirectory(prefix="openbim-ifc-bundle-mutation-") as directory:
        candidate = Path(directory) / "openbim.ifc"
        shutil.copytree(ROOT / "packages/openbim.ifc", candidate)
        replace_once(
            candidate / "Catalog.pkl",
            '  externalTypeSystem = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3"',
            '  externalTypeSystem = "https://example.invalid/broken-ifc-identity"',
        )
        replace_once(
            candidate / "Catalog.pkl",
            '  if (\n    !hasEntity("IFC2X3_TC1", name_)\n      && !hasEntity("IFC4_ADD2_TC1", name_)\n      && !hasEntity("IFC4X3_ADD2", name_)\n  )',
            "  if (false)",
        )
        replace_once(
            candidate / "Catalog.pkl",
            "normativeLifecycleEvidence: List<ifc.LifecycleEvidence> = List()",
            'normativeLifecycleEvidence: List<ifc.LifecycleEvidence> = List(new ifc.LifecycleEvidence { entity = "IfcWall"; kind = "introduced"; release = "IFC4_ADD2_TC1"; sourceUri = "https://example.invalid/unsupported" })',
        )
        replace_once(
            candidate / "ifc.pkl",
            '  continuityPolicy: "explicit-evidence-required"',
            '  continuityPolicy: "explicit-evidence-required" | "name-equality"',
        )
        replace_once(
            candidate / "ifc.pkl",
            '  continuityPolicy = "explicit-evidence-required"',
            '  continuityPolicy = "name-equality"',
        )
        replace_once(
            candidate / "internal/Ifc4Data.pkl",
            '  ["IfcWall"] = new ifc.DirectEntityDefinition {\n    parent = "IfcBuildingElement"\n    attributes = List("PredefinedType")',
            '  ["IfcWall"] = new ifc.DirectEntityDefinition {\n    parent = "IfcElement"\n    attributes = List("PredefinedType")',
        )
        replace_once(
            candidate / "internal/Ifc4x3Data.pkl",
            'ifc4x3Removed: List<String> =\n  List(\n    "IfcBeamStandardCase",\n    "IfcBuildingElement",\n    "IfcBuildingElementType",',
            'ifc4x3Removed: List<String> =\n  List(\n    "IfcBeamStandardCase",\n    "IfcBuildingElementType",',
        )
        replace_once(
            candidate / "internal/TemplateIfc4Data.pkl",
            'sourceGuid = "76903c80d1dc11e1800000215ad4efdf"',
            'sourceGuid = "00000000000000000000000000000000"',
        )
        replace_once(
            candidate / "internal/TemplateIfc4x3Data.pkl",
            'sourceGuid = "91e0ddf4d6ba45e3b689a10510bef4bc"',
            'sourceGuid = "ff20d400d20011e1800000215ad4efdf"',
        )
        replace_once(
            candidate / "internal/TemplateIfc4x3Data.pkl",
            'sourceGuid = "53651ee9f81d4642abbd27656122671a"',
            'sourceGuid = "0516b500d20111e1800000215ad4efdf"',
        )
        replace_once(
            candidate / "internal/TemplateIfc4x3Data.pkl",
            'sha256 = "704a4f7d52b06b1421b75f4f4cdb79603d4b05a5663f6315faf804e6b6c63e56"',
            'sha256 = "233989ec941aa014f9317f6cb13d73284b09b8138501571b3130c58d6c371eab"',
        )
        result = run_test(candidate, "tests/ifc.pkl")
        expected_failures = (
            "release references retain https type identity and package transport separately",
            "reconstructed ancestry and Part 21 attributes are inherited-first",
            "observed transitions are not normative lifecycle claims",
            "cross-version presence is exact and absent lookups fail closed",
            "template catalogs expose exact official release inventories",
            "official IFC4 property references are set-scoped and typed",
            "same-name set evolution preserves changed release-local occurrences",
            "member evolution preserves changed release-local property occurrences",
            "unchanged structures are inherited while provenance remains release-local",
        )
        missing = [name for name in expected_failures if name not in result.stdout]
        if result.returncode == 0 or missing:
            raise SystemExit(
                "mutation gate failed: bundled IFC regressions were not independently rejected; "
                f"missing facts={missing}\n{result.stdout[-4000:]}"
            )
        print(f"mutation rejected: ifc-bundle ({len(expected_failures)} independent facts)")


def main() -> None:
    expect_rejected(
        "loin-cardinality", "openbim.loin", "tests/loin.pkl",
        lambda package: replace_once(
            package / "loin.pkl", "specifications: Listing<Specification>(isNotEmpty)",
            "specifications: Listing<Specification>",
        ),
    )
    expect_rejected(
        "geometry-capability-id", "openbim.geometry", "tests/geometry.pkl",
        lambda package: replace_once(
            package / "capabilities/Representation.pkl",
            '"openbim.geometry:representation.brep.trimmed-analytic"',
            '"openbim.geometry:representation.brep.trimmed-analytic-broken"',
        ),
    )
    expect_ifc_bundle_rejected()


if __name__ == "__main__":
    main()
