#!/usr/bin/env python3
"""Prove the package tests detect representative semantic regressions."""

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
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(
            f"mutation gate failed: expected one marker in {path}, got {text.count(old)}"
        )
    path.write_text(text.replace(old, new))


def expect_rejected(label: str, package: str, test: str, mutation) -> None:
    with tempfile.TemporaryDirectory(prefix=f"openbim-{label}-mutation-") as directory:
        candidate = Path(directory) / package
        shutil.copytree(ROOT / "packages" / package, candidate)
        mutation(candidate)
        result = subprocess.run(
            [PKL, "test", str(candidate / test)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode == 0:
            raise SystemExit(f"mutation gate failed: {label} regression survived")
        print(f"mutation rejected: {label}")


def main() -> None:
    expect_rejected(
        "loin-cardinality",
        "openbim.loin",
        "tests/loin.pkl",
        lambda package: replace_once(
            package / "loin.pkl",
            "specifications: Listing<Specification>(isNotEmpty)",
            "specifications: Listing<Specification>",
        ),
    )
    expect_rejected(
        "geometry-capability-id",
        "openbim.geometry",
        "tests/geometry.pkl",
        lambda package: replace_once(
            package / "capabilities/Representation.pkl",
            '"openbim.geometry:representation.brep.trimmed-analytic"',
            '"openbim.geometry:representation.brep.trimmed-analytic-broken"',
        ),
    )
    expect_rejected(
        "ifc-release-identity",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "Catalog.pkl",
            '  externalTypeSystem = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3"',
            '  externalTypeSystem = "package://broken-ifc-identity"',
        ),
    )
    expect_rejected(
        "ifc-resolver-guard",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "Catalog.pkl",
            '  if (\n    !hasEntity("IFC2X3_TC1", name_)\n      && !hasEntity("IFC4_ADD2_TC1", name_)\n      && !hasEntity("IFC4X3_ADD2", name_)\n  )',
            "  if (false)",
        ),
    )
    expect_rejected(
        "ifc-lifecycle-evidence",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "Catalog.pkl",
            "normativeLifecycleEvidence: List<ifc.LifecycleEvidence> = List()",
            'normativeLifecycleEvidence: List<ifc.LifecycleEvidence> = List(new ifc.LifecycleEvidence { entity = "IfcWall"; kind = "introduced"; release = "IFC4_ADD2_TC1"; sourceUri = "https://example.invalid/unsupported" })',
        ),
    )
    expect_rejected(
        "ifc-template-continuity-boundary",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "ifc.pkl",
            '  continuityPolicy = "explicit-evidence-required"',
            '  continuityPolicy = "name-equality"',
        ),
    )
    expect_rejected(
        "ifc-direct-declaration",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "Catalog.pkl",
            '  ["IfcWall"] = new ifc.DirectEntityDefinition {\n    parent = "IfcBuildingElement"\n    attributes = List("PredefinedType")',
            '  ["IfcWall"] = new ifc.DirectEntityDefinition {\n    parent = "IfcElement"\n    attributes = List("PredefinedType")',
        ),
    )
    expect_rejected(
        "ifc-release-membership",
        "openbim.ifc",
        "tests/ifc.pkl",
        lambda package: replace_once(
            package / "Catalog.pkl",
            'ifc4x3Removed: List<String> =\n  List(\n    "IfcBeamStandardCase",\n    "IfcBuildingElement",\n    "IfcBuildingElementType",',
            'ifc4x3Removed: List<String> =\n  List(\n    "IfcBeamStandardCase",\n    "IfcBuildingElementType",',
        ),
    )


if __name__ == "__main__":
    main()
