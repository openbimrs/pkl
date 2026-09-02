# IFC structural catalogs

`openbim.ifc` is a release-explicit Apple Pkl package for authoring references to IFC schema structure. Version `0.2.1` covers the exact bundled releases used by `openbimrs/ifc`:

| Entry point | Release | Entities | Defined types |
|---|---|---:|---:|
| `versions/Ifc2x3.pkl` | IFC2X3 TC1 | 653 | 327 |
| `versions/Ifc4.pkl` | IFC4 ADD2 TC1 | 776 | 397 |
| `versions/Ifc4x3.pkl` | IFC4X3 ADD2 | 876 | 436 |

The three entry points are thin views over one delta-compressed catalog:

- one 1,006-name `EntityName` union catches unknown spellings;
- IFC2X3 stores the baseline direct declarations;
- IFC4 and IFC4X3 store only additions, removals, and changed direct declarations;
- ancestry and inherited-first Part 21 attributes are reconstructed for the selected release;
- `entity` and `entityByName` fail closed when a known name is absent from that release;
- every result retains its exact release, HTTPS external type-system identity, and separate package transport URI.

```pkl
import "@ifc/versions/Ifc4x3.pkl" as ifc4x3

wall = ifc4x3.entity("IfcWall")
amendedSupertype = wall.directSupertype
inheritedSlots = wall.attributes
```

`Catalog.pkl` is a small generated facade over cohesive generated modules in
`internal/`: names, the IFC2X3 baseline, IFC4 and IFC4X3 deltas, and observed
transitions. This physical split keeps generated diffs reviewable; it does not
change the resolver API or duplicate expanded release snapshots. Pkl does not
enforce module visibility, so `internal/` paths are technically importable but
carry no compatibility guarantee. Consumers must import `Catalog.pkl` or a
release module under `versions/`.

`Catalog.pkl` also exposes exact observed additions and removals between the supported snapshots. Those differences are not presented as normative introduction, deprecation, rename, or replacement claims. Such lifecycle claims require separately sourced `LifecycleEvidence` records.

## Provenance boundary

Direct structural rows are deterministically exported from the bundled `ifc-schema` artifacts in `openbimrs/ifc`; Pkl does not infer declarations from specification prose. Each TSV row contains only an entity name, immediate parent, and directly declared positional slots. The canonical Rust export tests reconstruct every expanded release row exactly.

The package pins artifact/exporter commits and SHA-256 digests under `packages/openbim.ifc/provenance/`. Frozen TSV evidence is excluded from the package ZIP. `NOTICE` records buildingSMART attribution.

The catalog contains structural facts only. It does not redistribute EXPRESS, XSD, prose, diagrams, or PSD/QTO XML.

## PSD/QTO extension boundary

Version `0.2.1` retains the structural and template boundary introduced in `0.2.0`, which removed the unverified free-form `propertySet` and `property` helpers from `0.1.0`. They made names release-bound but could not prove that a set/member existed in the selected template edition.

Typed property-set and quantity-set evolution must come from deterministic exports owned by the canonical Rust `ifc-template-catalog`. The typed extension boundary fixes occurrence identity as release-local and requires explicit continuity evidence; shared names or GUIDs are candidates, not proof. Snapshot presence and normative lifecycle evidence remain distinct. Until package-owned runtime references are bundled, downstream consumers must omit IFC template identity claims rather than substitute local strings; MCS must never define its own IFC template schema.

## Boundary with MCS and geometry

- IFC owns release identity, structural names, declarations, and eventually typed template catalogs.
- `openbim.geometry` owns exact atomic geometry capability identifiers.
- Axioval MCS owns normalized rules, applicability, parameters, and citations.
- MCS adapters lower package-owned values without copying either specialized catalog.

Package transport URIs identify where Pkl code is fetched. They are never emitted as the normalized external IFC type system.
