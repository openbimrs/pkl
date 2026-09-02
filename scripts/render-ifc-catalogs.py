#!/usr/bin/env python3
"""Render delta-compressed Pkl IFC catalogs from frozen structural TSVs."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from ifc_catalog_modules import GENERATED_MARKER, write_modules


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
    external_type_system: str
    header_tokens: tuple[str, ...]


EDITIONS = (
    Edition("ifc2x3.tsv", "Ifc2x3.pkl", "ifc2x3", "IFC2X3_TC1", "IFC2x3 TC1", 653, 327,
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/",
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/", ("IFC2X3",)),
    Edition("ifc4.tsv", "Ifc4.pkl", "ifc4", "IFC4_ADD2_TC1", "IFC4 ADD2 TC1", 776, 397,
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/",
            "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4", ("IFC4",)),
    Edition("ifc4x3.tsv", "Ifc4x3.pkl", "ifc4x3", "IFC4X3_ADD2", "IFC4X3 ADD2", 876, 436,
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/",
            "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3", ("IFC4X3", "IFC4X3_ADD2")),
)

DirectDefinition = tuple[str | None, tuple[str, ...]]


def pkl_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def pkl_list(values: tuple[str, ...] | list[str]) -> str:
    return "List(" + ", ".join(pkl_string(value) for value in values) + ")"


def parse_sequence(value: str) -> tuple[str, ...]:
    return () if value == "-" else tuple(item for item in value.split(",") if item)


def read_catalog(path: Path, edition: Edition) -> dict[str, DirectDefinition]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[:2] != ["# openbim.ifc direct-structural-catalog v1", f"schema\t{edition.release_id}\t{edition.entity_count}\t{edition.type_count}"]:
        raise SystemExit(f"unexpected catalog header: {path}")
    rows: dict[str, DirectDefinition] = {}
    for number, line in enumerate(lines[2:], start=3):
        fields = line.split("\t")
        if len(fields) != 4 or fields[0] != "entity":
            raise SystemExit(f"invalid row {path}:{number}")
        name = fields[1]
        parent = None if fields[2] == "-" else fields[2]
        attributes = parse_sequence(fields[3])
        if not name.startswith("Ifc") or (parent is not None and not parent.startswith("Ifc")):
            raise SystemExit(f"non-IFC entity identifier in {path}:{number}")
        if any(not attribute or not attribute.replace("_", "").isalnum() for attribute in attributes):
            raise SystemExit(f"invalid attribute identifier in {path}:{number}")
        if name in rows:
            raise SystemExit(f"duplicate entity {name} in {path}")
        rows[name] = (parent, attributes)
    if len(rows) != edition.entity_count or list(rows) != sorted(rows):
        raise SystemExit(f"catalog rows are not sorted and exact for {path}")
    validate_declarations(path, rows)
    return rows


def validate_declarations(path: Path, rows: dict[str, DirectDefinition]) -> None:
    """Reject missing parents, duplicate slots, and cyclic direct ancestry."""
    parents = {name: parent for name, (parent, _) in rows.items()}
    for name, (parent, attributes) in rows.items():
        if parent is not None and parent not in rows:
            raise SystemExit(f"missing immediate parent {parent} for {name} in {path}")
        if len(attributes) != len(set(attributes)):
            raise SystemExit(f"duplicate directly declared attribute for {name} in {path}")
    for name in rows:
        seen: set[str] = set()
        current: str | None = name
        while current is not None:
            if current in seen:
                raise SystemExit(f"cyclic immediate parent graph at {name} in {path}")
            seen.add(current)
            current = parents[current]


def pkl_definition(name: str, direct: tuple[str | None, tuple[str, ...]]) -> str:
    parent, attributes = direct
    parent_value = "null" if parent is None else pkl_string(parent)
    return "\n".join((
        f"  [{pkl_string(name)}] = new ifc.DirectEntityDefinition {{",
        f"    parent = {parent_value}",
        f"    attributes = {pkl_list(attributes)}",
        "  }",
    ))


def pkl_mapping(rows: dict[str, tuple[str | None, tuple[str, ...]]]) -> str:
    return "\n".join(pkl_definition(name, direct) for name, direct in rows.items())


def render_catalog(
    editions: tuple[Edition, ...],
    catalogs: list[dict[str, DirectDefinition]],
    digests: list[str],
    source_commit: str,
    package_version: str,
) -> str:
    directs = catalogs
    baseline = directs[0]
    delta4 = {name: direct for name, direct in directs[1].items() if baseline.get(name) != direct}
    removed4 = sorted(set(baseline) - set(directs[1]))
    delta4x3 = {name: direct for name, direct in directs[2].items() if directs[1].get(name) != direct}
    removed4x3 = sorted(set(directs[1]) - set(directs[2]))
    revisions = len(baseline) + len(delta4) + len(delta4x3)
    if (len(delta4), len(removed4), len(delta4x3), len(removed4x3), revisions) != (399, 114, 184, 16, 1236):
        raise SystemExit("unexpected delta metrics; frozen TSVs or direct-declaration factoring changed")
    names = sorted(set().union(*catalogs))
    added4 = sorted(set(catalogs[1]) - set(catalogs[0]))
    added4x3 = sorted(set(catalogs[2]) - set(catalogs[1]))
    if (len(names), len(added4), len(added4x3)) != (1006, 237, 116):
        raise SystemExit("unexpected union/transition metrics; frozen TSVs changed")
    aliases = "\n".join(("  " if index == 0 else "    | ") + pkl_string(name) for index, name in enumerate(names))
    releases = "\n\n".join(
        f'''{edition.module_name}Release: ifc.Release = new ifc.Release {{
  id = "{edition.release_id}"
  label = "{edition.label}"
  headerTokens = {pkl_list(edition.header_tokens)}
  entityCount = {edition.entity_count}
  typeCount = {edition.type_count}
  sourceUri = "{edition.source_uri}"
  externalTypeSystem = "{edition.external_type_system}"
  packageCatalogUri = "package://openbimrs.github.io/pkl/openbim.ifc@{package_version}#/releases/{edition.release_id}"
}}''' for edition in editions
    )
    return f'''{GENERATED_MARKER}
/// Generated delta-compressed IFC evolution catalog; do not edit by hand.
/// Source `openbimrs/ifc` commit: {source_commit}
/// Structural TSV SHA-256: IFC2X3={digests[0]}, IFC4={digests[1]}, IFC4X3={digests[2]}
module openbim.ifc.Catalog

import "./ifc.pkl" as ifc

{releases}

/// Closed union across all supported snapshots; resolver availability remains release-bound.
typealias EntityName =
{aliases}

entityNames: List<EntityName> = {pkl_list(names)}
revisionCount: UInt = {revisions}
directDeclarationCount: UInt = {revisions}

/// IFC2X3 is the physical baseline; entries are immediate parent plus directly declared slots.
ifc2x3Baseline: Mapping<String, ifc.DirectEntityDefinition> = new {{
{pkl_mapping(baseline)}
}}

/// IFC4 only stores additions and changed direct declarations relative to IFC2X3.
ifc4Delta: Mapping<String, ifc.DirectEntityDefinition> = new {{
{pkl_mapping(delta4)}
}}
ifc4Removed: List<String> = {pkl_list(removed4)}

/// IFC4X3 only stores additions and changed direct declarations relative to IFC4.
ifc4x3Delta: Mapping<String, ifc.DirectEntityDefinition> = new {{
{pkl_mapping(delta4x3)}
}}
ifc4x3Removed: List<String> = {pkl_list(removed4x3)}

/// Observed supported-snapshot transitions only; these make no normative lifecycle claim.
ifc4ObservedAdded: List<String> = {pkl_list(added4)}
ifc4ObservedRemoved: List<String> = {pkl_list(removed4)}
ifc4x3ObservedAdded: List<String> = {pkl_list(added4x3)}
ifc4x3ObservedRemoved: List<String> = {pkl_list(removed4x3)}

/// Normative lifecycle evidence is intentionally empty until a sourced changelog exporter supplies it.
normativeLifecycleEvidence: List<ifc.LifecycleEvidence> = List()
lifecycleEvidence = normativeLifecycleEvidence

function releaseFor(id: ifc.ReleaseId): ifc.Release =
  if (id == "IFC2X3_TC1") ifc2x3Release
  else if (id == "IFC4_ADD2_TC1") ifc4Release
  else ifc4x3Release

function hasEntity(release: ifc.ReleaseId, name: String): Boolean =
  if (release == "IFC2X3_TC1") ifc2x3Baseline.containsKey(name)
  else if (release == "IFC4_ADD2_TC1")
    !ifc4Removed.contains(name) && (ifc4Delta.containsKey(name) || ifc2x3Baseline.containsKey(name))
  else
    !ifc4x3Removed.contains(name)
      && (ifc4x3Delta.containsKey(name) || hasEntity("IFC4_ADD2_TC1", name))

function directDefinition(release: ifc.ReleaseId, name: String): ifc.DirectEntityDefinition =
  if (release == "IFC2X3_TC1") ifc2x3Baseline[name]
  else if (release == "IFC4_ADD2_TC1")
    if (ifc4Removed.contains(name)) throw("entity is absent from IFC4: \\(name)")
    else if (ifc4Delta.containsKey(name)) ifc4Delta[name]
    else ifc2x3Baseline[name]
  else if (ifc4x3Removed.contains(name)) throw("entity is absent from IFC4X3: \\(name)")
  else if (ifc4x3Delta.containsKey(name)) ifc4x3Delta[name]
  else directDefinition("IFC4_ADD2_TC1", name)

function ancestry(release: ifc.ReleaseId, definition: ifc.DirectEntityDefinition): List<String> =
  if (definition.parent == null) List()
  else List(definition.parent) + ancestry(release, directDefinition(release, definition.parent))

function attributes(release: ifc.ReleaseId, definition: ifc.DirectEntityDefinition): List<String> =
  if (definition.parent == null) definition.attributes
  else attributes(release, directDefinition(release, definition.parent)) + definition.attributes

function entity(release_: ifc.ReleaseId, name_: String): ifc.EntityReference =
  let (definition = directDefinition(release_, name_))
    new ifc.EntityReference {{
      release = release_
      externalTypeSystem = releaseFor(release_).externalTypeSystem
      packageCatalogUri = releaseFor(release_).packageCatalogUri
      name = name_
      directSupertype = definition.parent
      directAttributes = definition.attributes
      supertypes = ancestry(release_, definition)
      attributes = attributes(release_, definition)
    }}

function definitionsFor(name: String): Mapping<ifc.ReleaseId, ifc.DirectEntityDefinition> = new {{
  when (hasEntity("IFC2X3_TC1", name)) {{ ["IFC2X3_TC1"] = directDefinition("IFC2X3_TC1", name) }}
  when (hasEntity("IFC4_ADD2_TC1", name)) {{ ["IFC4_ADD2_TC1"] = directDefinition("IFC4_ADD2_TC1", name) }}
  when (hasEntity("IFC4X3_ADD2", name)) {{ ["IFC4X3_ADD2"] = directDefinition("IFC4X3_ADD2", name) }}
}}

function observedAdded(release: ifc.ReleaseId): List<String> =
  if (release == "IFC4_ADD2_TC1") ifc4ObservedAdded
  else if (release == "IFC4X3_ADD2") ifc4x3ObservedAdded
  else List()

function observedRemoved(release: ifc.ReleaseId): List<String> =
  if (release == "IFC4_ADD2_TC1") ifc4ObservedRemoved
  else if (release == "IFC4X3_ADD2") ifc4x3ObservedRemoved
  else List()

function evolution(name_: EntityName): ifc.EntityEvolution = evolutionByName(name_)

function evolutionByName(name_: String): ifc.EntityEvolution =
  if (!hasEntity("IFC2X3_TC1", name_) && !hasEntity("IFC4_ADD2_TC1", name_) && !hasEntity("IFC4X3_ADD2", name_))
    throw("unknown IFC entity: \\(name_)")
  else new ifc.EntityEvolution {{
    name = name_
    definitions = definitionsFor(name_)
    observedAddedIn =
      (if (ifc4ObservedAdded.contains(name_)) List("IFC4_ADD2_TC1") else List())
        + (if (ifc4x3ObservedAdded.contains(name_)) List("IFC4X3_ADD2") else List())
    observedRemovedIn =
      (if (ifc4ObservedRemoved.contains(name_)) List("IFC4_ADD2_TC1") else List())
        + (if (ifc4x3ObservedRemoved.contains(name_)) List("IFC4X3_ADD2") else List())
    lifecycleEvidence = normativeLifecycleEvidence.filter((it) -> it.entity == name_)
  }}
'''


def render_wrapper(edition: Edition, digest: str, source_commit: str) -> str:
    return f'''{GENERATED_MARKER}
/// Thin {edition.label} view over the generated delta-compressed evolution catalog.
/// Source `openbimrs/ifc` commit: {source_commit}; structural TSV SHA-256: {digest}
module openbim.ifc.versions.{edition.module_name}

import "../ifc.pkl" as ifc
import "../Catalog.pkl" as catalog

release: ifc.Release = catalog.{edition.module_name}Release
typealias EntityName = catalog.EntityName

function entity(name_: EntityName): ifc.EntityReference = catalog.entity(release.id, name_)
function entityByName(name_: String): ifc.EntityReference = catalog.entity(release.id, name_)
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--package-version", required=True)
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(char not in "0123456789abcdef" for char in args.source_commit):
        raise SystemExit("--source-commit must be a full lowercase Git object ID")
    if not args.package_version or any(char not in "0123456789." for char in args.package_version):
        raise SystemExit("--package-version must be a numeric semantic version")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalogs = [read_catalog(args.source_dir / edition.input_name, edition) for edition in EDITIONS]
    digests = [hashlib.sha256((args.source_dir / edition.input_name).read_bytes()).hexdigest() for edition in EDITIONS]
    monolith = render_catalog(
        EDITIONS, catalogs, digests, args.source_commit, args.package_version
    )
    write_modules(monolith, args.output_dir)
    versions = args.output_dir / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    for edition, digest in zip(EDITIONS, digests, strict=True):
        (versions / edition.output_name).write_text(
            render_wrapper(edition, digest, args.source_commit), encoding="utf-8"
        )
    print(
        "wrote modular IFC catalog: modules=9 union=1006 "
        "revisions=1236 direct declarations=1236"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
