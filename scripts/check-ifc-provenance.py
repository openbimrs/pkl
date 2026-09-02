#!/usr/bin/env python3
"""Fail closed when IFC source snapshots or generated Pkl catalogs drift."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/openbim.ifc"
PROVENANCE = PACKAGE / "provenance"
CATALOGS = PROVENANCE / "catalogs"
TEMPLATES = PROVENANCE / "templates"
GENERATED = tuple(
    PACKAGE / relative
    for relative in (
        "Catalog.pkl",
        "TemplateCatalog.pkl",
        "internal/Names.pkl",
        "internal/Ifc2x3Data.pkl",
        "internal/Ifc4Data.pkl",
        "internal/Ifc4x3Data.pkl",
        "internal/Transitions.pkl",
        "internal/TemplateNames.pkl",
        "internal/TemplateIfc2x3Data.pkl",
        "internal/TemplateIfc4Data.pkl",
        "internal/TemplateIfc4x3Data.pkl",
        "internal/TemplateTransitions.pkl",
        "versions/Ifc2x3.pkl",
        "versions/Ifc4.pkl",
        "versions/Ifc4x3.pkl",
        "templates/Ifc2x3.pkl",
        "templates/Ifc4.pkl",
        "templates/Ifc4x3.pkl",
    )
)
EXPECTED_STRUCTURAL = {
    "repository": "https://github.com/openbimrs/ifc",
    "artifact_commit": "a7c4949bb941504ce874bdec13bd81d33491b5cb",
    "exporter_commit": "a97e8f7e646407d6a4263a664631a1877dfa2986",
    "ifc2x3_sha256": "8c89a84de9c603e9dfe713aa3f89f86347972cdaaefbf0a723137ef1c280d746",
    "ifc4_sha256": "51109c3295ecb17a38f8efdeca66bbd79d9d961719b20ba99888888b179ce5f6",
    "ifc4x3_sha256": "b00744442087c969f321550b3dcea7e49e0834ca001a4700ea5459e36eb56f12",
}
EXPECTED_TEMPLATES = {
    "repository": "https://github.com/openbimrs/ifc.git",
    "exporter_commit": "f378f824a3787a11218466a8c63ecd0984d0240b",
    "ifc2x3_sha256": "6950f7686b67b68d456e2dde0be9fcae83cbc7849171a1d2c9bf95d4b0718586",
    "ifc4_sha256": "15dca1204b3f7533b2ee85fe353ad1d9b23fdf318fcb46100bef45dd5c2eb42c",
    "ifc4x3_sha256": "11fb5c50dd87b78ccc3f5c09470942cc5d454760d07054d9b879fafe26a737c1",
}


def fail(message: str) -> None:
    raise SystemExit(f"IFC provenance check failed: {message}")


def read_env(path: Path, expected: set[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if not separator or not key or not value or key in result:
            fail(f"malformed or duplicate {path.relative_to(PROVENANCE)} entry")
        result[key] = value
    if result.keys() != expected:
        fail(f"{path.relative_to(PROVENANCE)} keys differ: {sorted(result)}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_plain_tree(root: Path, expected_names: set[str]) -> None:
    canonical_root = root.resolve(strict=True)
    observed = {entry.name for entry in os.scandir(root)}
    if observed != expected_names:
        fail(f"{root.relative_to(PROVENANCE)} entries differ: {sorted(observed)}")
    for name in sorted(expected_names):
        path = root / name
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
            fail(f"source input is not a plain file: {path.relative_to(PROVENANCE)}")
        if not path.resolve(strict=True).is_relative_to(canonical_root):
            fail(f"source input escapes its root: {path.relative_to(PROVENANCE)}")


def package_version() -> str:
    project = (PACKAGE / "PklProject").read_text(encoding="utf-8")
    match = re.search(r'^\s*version = "([0-9]+\.[0-9]+\.[0-9]+)"$', project, re.MULTILINE)
    if match is None:
        fail("PklProject has no numeric package version")
    return match.group(1)


def main() -> None:
    structural = read_env(
        PROVENANCE / "source.env",
        {"repository", "artifact_commit", "exporter_commit", "ifc2x3_sha256", "ifc4_sha256", "ifc4x3_sha256"},
    )
    templates = read_env(
        TEMPLATES / "source.env",
        {"repository", "exporter_commit", "ifc2x3_sha256", "ifc4_sha256", "ifc4x3_sha256"},
    )
    if structural != EXPECTED_STRUCTURAL:
        fail("structural source identity differs from the reviewed pin")
    if templates != EXPECTED_TEMPLATES:
        fail("template source identity differs from the reviewed pin")
    require_plain_tree(CATALOGS, {"ifc2x3.tsv", "ifc4.tsv", "ifc4x3.tsv"})
    require_plain_tree(
        TEMPLATES,
        {"source.env", "ifc2x3-tc1.tsv", "ifc4-add2-tc1.tsv", "ifc4x3-add2.tsv"},
    )
    for name in ("ifc2x3", "ifc4", "ifc4x3"):
        actual = digest(CATALOGS / f"{name}.tsv")
        if actual != structural[f"{name}_sha256"]:
            fail(f"catalog {name}.tsv digest {actual} does not match provenance")
    for name, file_name in (
        ("ifc2x3", "ifc2x3-tc1.tsv"),
        ("ifc4", "ifc4-add2-tc1.tsv"),
        ("ifc4x3", "ifc4x3-add2.tsv"),
    ):
        actual = digest(TEMPLATES / file_name)
        if actual != templates[f"{name}_sha256"]:
            fail(f"template {file_name} digest {actual} does not match provenance")

    renderer = (ROOT / "scripts/render-ifc-template-catalogs.py").read_text(encoding="utf-8")
    if f'SOURCE_COMMIT = "{templates["exporter_commit"]}"' not in renderer:
        fail("template renderer source commit differs from provenance")
    pkl = shutil.which("pkl")
    if pkl is None:
        fail("pkl is not on PATH")
    with tempfile.TemporaryDirectory(prefix="openbim-ifc-render-") as directory:
        rendered = Path(directory)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/render-ifc-catalogs.py"),
             "--source-dir", str(CATALOGS), "--output-dir", str(rendered),
             "--source-commit", structural["artifact_commit"],
             "--package-version", package_version()],
            cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/render-ifc-template-catalogs.py"),
             "--source-dir", str(TEMPLATES), "--output-dir", str(rendered),
             "--package-version", package_version()],
            cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
        )
        subprocess.run([pkl, "format", "-w", str(rendered)], check=True)
        expected_relatives = {path.relative_to(PACKAGE) for path in GENERATED}
        for expected in sorted(GENERATED):
            relative = expected.relative_to(PACKAGE)
            candidate = rendered / relative
            if not candidate.is_file() or candidate.read_bytes() != expected.read_bytes():
                fail(f"generated catalog drift: {relative}")
        extras = {path.relative_to(rendered) for path in rendered.rglob("*.pkl")} - expected_relatives
        if extras:
            fail(f"unexpected generated catalogs: {sorted(map(str, extras))}")

    print("verified IFC structural/template digests and deterministic Pkl catalogs")


if __name__ == "__main__":
    main()
