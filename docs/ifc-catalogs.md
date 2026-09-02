# IFC release catalogs

`openbim.ifc@0.3.0` is a release-explicit Apple Pkl package for authoring typed references to IFC entities, official property-set templates (PSD), quantity-set templates (QTO), and their members.

## Supported releases

| Entry point | Release | Entities | Defined types | PSD sets | QTO sets | Template members |
|---|---|---:|---:|---:|---:|---:|
| `versions/Ifc2x3.pkl` | IFC2X3 TC1 | 653 | 327 | 317 | 0 | 1,856 |
| `versions/Ifc4.pkl` | IFC4 ADD2 TC1 | 776 | 397 | 420 | 93 | 2,807 |
| `versions/Ifc4x3.pkl` | IFC4X3 ADD2 | 876 | 436 | 502 | 110 | 3,242 |

IFC2X3's official snapshot contains no QTO files. The package represents that as an empty quantity catalog instead of backfilling data from a later release.

## Public imports

Use an exact release for normal authoring:

```pkl
import "@ifc/versions/Ifc4.pkl" as ifc4
import "@ifc/templates/Ifc4.pkl" as ifc4Templates

wall = ifc4.entity("IfcWall")
doorCommon = ifc4Templates.propertySet("Pset_DoorCommon")
handicapAccessible = ifc4Templates.property("Pset_DoorCommon", "HandicapAccessible")
wallQuantities = ifc4Templates.quantitySet("Qto_WallBaseQuantities")
netVolume = ifc4Templates.quantity("Qto_WallBaseQuantities", "NetVolume")
```

The supported public surfaces are:

- `ifc.pkl`: shared typed contracts;
- `Catalog.pkl`: entity compatibility facade;
- `TemplateCatalog.pkl`: PSD/QTO catalog and evolution facade;
- `versions/Ifc2x3.pkl`, `versions/Ifc4.pkl`, and `versions/Ifc4x3.pkl`: unchanged entity-only release views;
- `templates/Ifc2x3.pkl`, `templates/Ifc4.pkl`, and `templates/Ifc4x3.pkl`: PSD/QTO release views.

Modules under `internal/` are generated storage and have no compatibility guarantee. The separate `templates/` views are deliberate: importing an existing entity-only `versions/` module does not parse the much larger PSD/QTO catalog.

Typed helpers accept closed unions of observed set names and member paths. The `*ByName` helpers accept dynamic strings but fail closed when a set is absent from the selected release, the PSD/QTO kind is wrong, or the member does not belong to that set.

## Entity evolution

The entity catalog has one 1,006-name union. IFC2X3 stores baseline direct declarations; IFC4 and IFC4X3 store additions, removals, and changed direct declarations. Ancestry and inherited-first Part 21 attributes are reconstructed for the selected release.

Observed additions and removals are snapshot differences, not normative introduction, deprecation, rename, or replacement claims. Those require separately sourced `LifecycleEvidence`.

## PSD/QTO evolution

The template catalog uses the same release-aware shape without conflating equal names with equal identities:

- IFC2X3 stores 317 direct set definitions;
- IFC4 stores 513 added or changed definitions;
- IFC4X3 stores 148 added or changed definitions: 109 additions and 39 changed same-name definitions;
- unchanged semantic definitions inherit from the nearest preceding snapshot;
- source-file path and SHA-256 provenance remain release-local even when semantics are inherited;
- each resolved set and member retains the selected IFC release, source GUID when present, owning set, exact member path, template/member kind, value type, and unit type.

`TemplateCatalog.pkl` exposes same-name observations across releases:

```pkl
import "@ifc/TemplateCatalog.pkl" as templates

riskHistory = templates.setEvolution("Pset_Risk")
riskTypeHistory = templates.memberEvolution("Pset_Risk", "RiskType")
```

`Pset_Risk` demonstrates why name equality is insufficient: its source GUID and structure differ between IFC4 ADD2 TC1 and IFC4X3 ADD2. `TemplateSetEvolution.definitions` therefore retains both release-local occurrences and records the observed change. `continuityEvidence` is empty unless an authoritative mapping is explicitly sourced; equal names or GUIDs alone do not populate it.

A member identity is set-scoped. `Pset_DoorCommon.HandicapAccessible` is not collapsed into a global `HandicapAccessible` string that could collide with a member of another set.

## Capability boundary

This is an official **reference catalog**, not a complete PSD/QTO XML object model. It bundles the normalized facts exported by canonical `openbimrs/ifc` tooling: set kind/name/GUID/template type, exact applicability clauses, member path/GUID/kind/value type/unit type, and source-file provenance. Localized descriptions, enumeration payloads, table payloads, and XML round-tripping are not claimed.

That boundary is sufficient for MCS to bind normalized concepts to official IFC set/member identities later without copying an IFC catalog. Detailed value-domain validation should use a future explicitly modeled capability rather than infer semantics absent from this export.

## Provenance

Entity rows come from deterministic `ifc-schema` exports. PSD/QTO rows come from the canonical Rust `ifc-template-catalog` exporter at `openbimrs/ifc` commit `f378f824a3787a11218466a8c63ecd0984d0240b`.

The package pins source commits and SHA-256 digests under `packages/openbim.ifc/provenance/`. Each public `TemplateCatalogRelease` also exposes the immutable exported-TSV `sourceUri`, `sourceSha256`, normalized `sourceDigest`, and `exporterCommit`. Frozen TSV evidence is excluded from the package ZIP. Generation checks reject source drift, unexpected files, symlinks, special files, path escapes, generated-topology drift, and byte differences from deterministic regeneration.

The template inputs contain 3,019 IFC2X3 rows, 3,525 IFC4 rows, and 4,361 IFC4X3 rows. `NOTICE` preserves buildingSMART attribution and CC BY-ND 4.0 terms for the deterministic format-shifted facts.

## Boundary with MCS and geometry

- IFC owns release identity, entity structure, official PSD/QTO references, and source provenance.
- `openbim.geometry` owns exact atomic geometry capability identifiers.
- Axioval MCS owns normalized rules, applicability, parameters, and citations.
- MCS adapters may lower package-owned references but must not copy IFC catalogs or add DIN-specific IFC schema logic.

Package URIs identify Pkl transport. Resolved references use the edition-specific HTTPS `externalTypeSystem` as semantic IFC identity; package transport URIs are never substituted for it.
