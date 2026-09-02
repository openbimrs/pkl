# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic versioning.

## [Unreleased]

## [0.3.0] - 2026-09-02

### Added

- Bundled official IFC2X3 TC1, IFC4 ADD2 TC1, and IFC4X3 ADD2 PSD/QTO
  reference catalogs with exact release inventories, set-scoped member identities,
  source GUIDs, applicability, value/unit types, and per-file provenance.
- Added `TemplateCatalog.pkl` plus release-view helpers for property sets,
  quantity sets, properties, quantities, dynamic fail-closed lookup, and same-name
  evolution inspection.
- Added deterministic template generation from checksum-pinned canonical
  `ifc-template-catalog` TSV exports and mutation evidence for identity,
  membership, provenance, delta, and continuity boundaries.

### Changed

- Advanced `openbim.ifc` to `0.3.0`; unchanged IFC4-to-IFC4X3 template
  definitions now inherit through a nearest-release delta while provenance stays
  release-local.
- Declared the package's aggregate upstream-data license as
  `AGPL-3.0-or-later AND CC-BY-ND-4.0` and expanded buildingSMART attribution.

### Security

- Template provenance checks reject checksum drift, unexpected entries,
  symlinks, special files, canonical-root escapes, generated topology changes,
  and nondeterministic regeneration.

## [0.2.1] - 2026-09-02

### Changed

- Refactored `openbim.ifc` into a 170-line stable catalog facade over generated
  name, baseline, delta, and transition modules without changing its
  release-explicit entity resolver contract.

## [0.2.0] - 2026-09-01

### Added

- Added a delta-compressed IFC2X3 baseline, IFC4/IFC4X3 direct-declaration
  deltas, one union resolver, thin version imports, deterministic regeneration,
  and explicit observed-versus-normative lifecycle boundaries.
- Added a typed, not-yet-bundled PSD/QTO extension boundary: occurrences remain
  release-local and cross-release continuity requires explicit evidence.

### Removed

- Removed unverified free-form property-set/property helpers; typed PSD/QTO
  references waited for canonical `ifc-template-catalog` data.

## [0.1.0] - 2026-09-01

### Added

- `openbim.loin` pure Apple Pkl package with the complete public LOIN semantic model.
- `openbim.ifc` exact IFC2X3 TC1, IFC4 ADD2 TC1, and IFC4X3 ADD2 entity catalogs.
- `openbim.geometry` vendor-neutral geometry capability vocabulary.
- Closed wire vocabularies, lexical contracts, schema cardinality constraints,
  deterministic provenance, complete examples, package tests, and remote consumer verification.

[Unreleased]: https://github.com/openbimrs/pkl/compare/openbim.ifc@0.3.0...HEAD
[0.3.0]: https://github.com/openbimrs/pkl/compare/openbim.ifc@0.2.1...openbim.ifc@0.3.0
[0.2.1]: https://github.com/openbimrs/pkl/compare/openbim.ifc@0.2.0...openbim.ifc@0.2.1
[0.2.0]: https://github.com/openbimrs/pkl/compare/openbim.ifc@0.1.0...openbim.ifc@0.2.0
[0.1.0]: https://github.com/openbimrs/pkl/releases/tag/openbim.loin@0.1.0
