#!/usr/bin/env python3
"""Render deterministic Pkl IFC catalogs from ifc-schema structural TSV."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Edition:
    input_name: str
    output_name: str
    module_name: str
    release_id: str
    label: str
    entity_count: int
    type_count: int
    source_uri: str
    header_tokens: tuple[str, ...]


EDITIONS = (
    Edition(
        "ifc2x3.tsv",
        "Ifc2x3.pkl",
        "ifc2x3",
        "IFC2X3_TC1",
        "IFC2x3 TC1",
        653,
        327,
        "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/",
        ("IFC2X3",),
    ),
    Edition(
        "ifc4.tsv",
        "Ifc4.pkl",
        "ifc4",
        "IFC4_ADD2_TC1",
        "IFC4 ADD2 TC1",
        776,
        397,
        "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/",
        ("IFC4",),
    ),
    Edition(
        "ifc4x3.tsv",
        "Ifc4x3.pkl",
        "ifc4x3",
        "IFC4X3_ADD2",
        "IFC4X3 ADD2",
        876,
        436,
        "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/",
        ("IFC4X3", "IFC4X3_ADD2"),
    ),
)


def pkl_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def pkl_list(values: tuple[str, ...]) -> str:
    return "List(" + ", ".join(pkl_string(value) for value in values) + ")"


def parse_sequence(value: str) -> tuple[str, ...]:
    if value == "-":
        return ()
    return tuple(item for item in value.split(",") if item)


def read_catalog(path: Path, edition: Edition) -> list[tuple[str, tuple[str, ...], tuple[str, ...]]]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if lines[:2] != [
        "# openbim.ifc structural-catalog v1",
        f"schema\t{edition.release_id}\t{edition.entity_count}\t{edition.type_count}",
    ]:
        raise SystemExit(f"unexpected catalog header: {path}")

    rows: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = []
    for line_number, line in enumerate(lines[2:], start=3):
        fields = line.split("\t")
        if len(fields) != 4 or fields[0] != "entity":
            raise SystemExit(f"invalid row {path}:{line_number}")
        name = fields[1]
        supertypes = parse_sequence(fields[2])
        attributes = parse_sequence(fields[3])
        if not name.startswith("Ifc") or any(
            not supertype.startswith("Ifc") for supertype in supertypes
        ):
            raise SystemExit(f"non-IFC entity identifier in {path}:{line_number}")
        if any(
            not attribute or not attribute.replace("_", "").isalnum()
            for attribute in attributes
        ):
            raise SystemExit(f"invalid attribute identifier in {path}:{line_number}")
        rows.append((name, supertypes, attributes))

    names = [row[0] for row in rows]
    if len(rows) != edition.entity_count:
        raise SystemExit(f"expected {edition.entity_count} rows in {path}, got {len(rows)}")
    if names != sorted(names) or len(names) != len(set(names)):
        raise SystemExit(f"catalog names are not sorted and unique: {path}")
    return rows


def render(edition: Edition, rows: list[tuple[str, tuple[str, ...], tuple[str, ...]]], digest: str, source_commit: str) -> str:
    aliases = "\n".join(
        ("  " if index == 0 else "    | ") + pkl_string(name)
        for index, (name, _, _) in enumerate(rows)
    )
    mappings: list[str] = []
    for name, supertypes, attributes in rows:
        mappings.extend(
            (
                f"  [{pkl_string(name)}] = new ifc.EntityDefinition {{",
                f"    supertypes = {pkl_list(supertypes)}",
                f"    attributes = {pkl_list(attributes)}",
                "  }",
            )
        )
    token_list = pkl_list(edition.header_tokens)
    catalog_type_system = (
        "package://openbimrs.github.io/pkl/openbim.ifc@0.1.0#/releases/"
        + edition.release_id
    )
    return f'''/// Generated structural facts for {edition.label}; do not edit by hand.
/// Source `openbimrs/ifc` commit: {source_commit}
/// Structural TSV SHA-256: {digest}
module openbim.ifc.versions.{edition.module_name}

import "../ifc.pkl" as ifc

schemaRelease: ifc.Release = new ifc.Release {{
  id = "{edition.release_id}"
  label = "{edition.label}"
  headerTokens = {token_list}
  entityCount = {edition.entity_count}
  typeCount = {edition.type_count}
  sourceUri = "{edition.source_uri}"
  catalogTypeSystem = "{catalog_type_system}"
}}

release: ifc.Release = schemaRelease

typealias EntityName =
{aliases}

entities: Mapping<String, ifc.EntityDefinition> = new {{
{chr(10).join(mappings)}
}}

function entity(name_: EntityName): ifc.EntityReference = entityByName(name_)

function entityByName(name_: String): ifc.EntityReference =
  let (definition = entities[name_])
    new ifc.EntityReference {{
      release = schemaRelease.id
      catalogTypeSystem = schemaRelease.catalogTypeSystem
      name = name_
      supertypes = definition.supertypes
      attributes = definition.attributes
    }}

function propertySet(name_: String): ifc.PropertySetReference =
  new ifc.PropertySetReference {{
    release = schemaRelease.id
    catalogTypeSystem = schemaRelease.catalogTypeSystem
    name = name_
  }}

function property(container_: String, name_: String): ifc.PropertyReference =
  new ifc.PropertyReference {{
    release = schemaRelease.id
    catalogTypeSystem = schemaRelease.catalogTypeSystem
    container = container_
    name = name_
  }}
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(char not in "0123456789abcdef" for char in args.source_commit):
        raise SystemExit("--source-commit must be a full lowercase Git object ID")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for edition in EDITIONS:
        source = args.source_dir / edition.input_name
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        rows = read_catalog(source, edition)
        target = args.output_dir / edition.output_name
        target.write_text(render(edition, rows, digest, args.source_commit), encoding="utf-8")
        print(f"wrote {target}: {len(rows)} rows, sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
