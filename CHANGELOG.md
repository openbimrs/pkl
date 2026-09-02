# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic versioning.

## [Unreleased]

### Added

- Added `openbim.ifc` 0.2.0 with a delta-compressed IFC2X3 baseline,
  IFC4/IFC4X3 direct-declaration deltas, one union resolver, thin version
  imports, deterministic regeneration, and explicit observed-versus-normative
  lifecycle boundaries.
- Added a typed, not-yet-bundled PSD/QTO extension boundary: occurrences remain
  release-local and cross-release continuity requires explicit evidence.
- Added `openbim.ifc` 0.1.0 with exact IFC2X3 TC1, IFC4 ADD2 TC1, and
  IFC4X3 ADD2 entity catalogs, inheritance closures, inherited attribute order,
  explicit release references, deterministic provenance, and MCS-ready adapters.
- Added `openbim.geometry` 0.1.0 with vendor-neutral capability IDs, scoped
  manifests, requirements, and declarative conformance reports.

### Changed

- Resolve and evaluate the published `openbim.loin@0.1.0` remote consumer in
  the repository gate.
- Create the Pkl installation directory on fresh CI runners.

### Removed

- Removed `openbim.ifc`'s unverified free-form property-set/property helpers;
  typed PSD/QTO references now wait for canonical `ifc-template-catalog` data.

## [0.1.0] - 2026-09-01

### Added

- `openbim.loin` pure Apple Pkl package with the complete public LOIN semantic model.
- Closed wire vocabularies, lexical GUID/language/date-time/email contracts, and schema cardinality constraints.
- Explicit partial ISO 23387 boundary for types imported by LOIN.
- Complete synthetic authoring example, module tests, package verification, and `Project.RemoteDependency` usage documentation.

[Unreleased]: https://github.com/openbimrs/pkl/compare/openbim.loin@0.1.0...HEAD
[0.1.0]: https://github.com/openbimrs/pkl/releases/tag/openbim.loin@0.1.0
