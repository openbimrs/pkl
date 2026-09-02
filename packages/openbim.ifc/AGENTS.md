# openbim.ifc package instructions

Versioned, schema-as-data Apple Pkl contracts generated from `openbimrs/ifc`'s `ifc-schema` artifacts.

- `ifc.pkl` owns neutral release/reference types.
- `versions/` contains generated, release-separated entity catalogs.
- `tests/` proves release identity, counts, inheritance, attributes, and fail-closed lookups.
- `provenance/` records source commit, catalog digests, and third-party attribution.

Never copy normative EXPRESS or specification prose. Generated catalogs may contain only structural names, ancestry, and positional attribute names. Never substitute one IFC version for another.
