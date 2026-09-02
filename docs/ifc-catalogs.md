# IFC structural catalogs

`openbim.ifc` is a version-separated Apple Pkl package for authoring references
to IFC schema structure. It covers the exact bundled releases used by
`openbimrs/ifc`:

| Module | Release | Entities | Defined types |
|---|---|---:|---:|
| `versions/Ifc2x3.pkl` | IFC2X3 TC1 | 653 | 327 |
| `versions/Ifc4.pkl` | IFC4 ADD2 TC1 | 776 | 397 |
| `versions/Ifc4x3.pkl` | IFC4X3 ADD2 | 876 | 436 |

Each version module exposes:

- a closed `EntityName` union;
- a deterministic entity map with complete supertype closure and inherited
  positional attribute order;
- `entity` for statically checked names and `entityByName` for fail-closed
  dynamic lookup;
- version-bound attribute, property-set, and property references.

```pkl
import "@ifc/versions/Ifc4x3.pkl" as ifc4x3

wall = ifc4x3.entity("IfcWall")
loadBearing = ifc4x3.property("Pset_WallCommon", "LoadBearing")
```

## Provenance boundary

The structural rows are deterministically generated from the bundled
`ifc-schema` artifacts in `openbimrs/ifc`, not transcribed in Pkl. The package
tracks the neutral TSV exports and their SHA-256 digests under
`packages/openbim.ifc/provenance/`; they are excluded from the package ZIP.
`NOTICE` records the exact artifact commit and buildingSMART attribution.

The catalog contains structural facts only. It does not redistribute EXPRESS,
XSD, specification prose, diagrams, or a complete PSD/QTO template catalog.
Consequently `propertySet` and `property` preserve explicit version-bound names
but do **not** claim that those names were verified against a bundled template
edition. Entity and inherited-attribute references are catalog-validated.

## Boundary with MCS and geometry

- IFC owns release identities, entity names, inheritance, attributes, and
  external template-reference encoding.
- `openbim.geometry` owns kernel capability IDs, exactness, requirements, and
  scoped conformance.
- Axioval MCS owns rules, applicability, parameters, citations, and normalized
  transport. Its adapters lower package-owned references without copying either
  catalog.

This keeps schema facts and geometric capabilities out of rule packages while
preserving version and scope information at the authoring boundary.
