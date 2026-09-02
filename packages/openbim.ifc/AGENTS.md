# openbim.ifc package instructions

Versioned, schema-as-data Apple Pkl contracts generated from `openbimrs/ifc`'s `ifc-schema` artifacts.

- `ifc.pkl` owns neutral release/reference types.
- `Catalog.pkl` is the generated stable resolver facade over delta-compressed data.
- `internal/` contains generated physical storage modules: the IFC2X3 baseline,
  IFC4/IFC4X3 deltas, the closed name set, and observed transitions. These modules
  are package implementation details even though Pkl does not enforce visibility.
- `versions/` contains thin release-specific resolver imports.
- `tests/` proves release identity, counts, direct revision metrics, reconstructed inheritance/attributes, lifecycle boundaries, and fail-closed lookups.
- `provenance/` records source commit, catalog digests, and third-party attribution.

Never copy normative EXPRESS or specification prose. Provenance catalogs contain
only structural names, immediate parents, and directly declared positional
attributes. Never substitute one IFC version for another.
