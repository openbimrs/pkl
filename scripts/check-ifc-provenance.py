#!/usr/bin/env python3
"""Fail closed when IFC source snapshots or generated Pkl catalogs drift."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/openbim.ifc"
PROVENANCE = PACKAGE / "provenance"
CATALOGS = PROVENANCE / "catalogs"
GENERATED = (PACKAGE / "Catalog.pkl", *(PACKAGE / "versions").glob("*.pkl"))


def fail(message: str) -> None:
    raise SystemExit(f"IFC provenance check failed: {message}")


def read_source() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in (PROVENANCE / "source.env").read_text().splitlines():
        key, separator, value = line.partition("=")
        if not separator or not key or not value or key in result:
            fail("malformed or duplicate source.env entry")
        result[key] = value
    expected = {
        "repository",
        "artifact_commit",
        "exporter_commit",
        "ifc2x3_sha256",
        "ifc4_sha256",
        "ifc4x3_sha256",
    }
    if result.keys() != expected:
        fail(f"source.env keys differ: {sorted(result.keys())}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = read_source()
    for name in ("ifc2x3", "ifc4", "ifc4x3"):
        actual = digest(CATALOGS / f"{name}.tsv")
        if actual != source[f"{name}_sha256"]:
            fail(f"{name}.tsv digest {actual} does not match provenance")

    pkl = shutil.which("pkl")
    if pkl is None:
        fail("pkl is not on PATH")
    with tempfile.TemporaryDirectory(prefix="openbim-ifc-render-") as directory:
        rendered = Path(directory)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/render-ifc-catalogs.py"),
                "--source-dir",
                str(CATALOGS),
                "--output-dir",
                str(rendered),
                "--source-commit",
                source["artifact_commit"],
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run([pkl, "format", "-w", str(rendered)], check=True)
        for expected in sorted(GENERATED):
            candidate = rendered / expected.name
            if not candidate.is_file() or candidate.read_bytes() != expected.read_bytes():
                fail(f"generated catalog drift: {expected.name}")
        extras = {path.name for path in rendered.glob("*.pkl")} - {
            path.name for path in GENERATED
        }
        if extras:
            fail(f"unexpected generated catalogs: {sorted(extras)}")

    print("verified IFC source digests and deterministic Pkl catalogs")


if __name__ == "__main__":
    main()
