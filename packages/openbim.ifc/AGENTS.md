# openbim.ifc package instructions

Release-explicit schema-as-data Apple Pkl contracts generated from canonical `openbimrs/ifc` exporters.

- `ifc.pkl` owns neutral release, entity, template-set, member, provenance, and evolution types.
- `Catalog.pkl` is the generated stable entity resolver facade.
- `TemplateCatalog.pkl` is the generated stable PSD/QTO resolver and evolution facade.
- `internal/` contains generated entity/template baseline, delta, name, provenance, and transition storage. These modules are unsupported implementation details even though Pkl does not enforce visibility.
- `versions/` contains thin, stable entity-only release views; template parsing must remain opt-in.
- `templates/` contains thin, stable PSD/QTO release views.
- `tests/` proves release identity, exact inventories, delta reconstruction, set-scoped member identity, provenance, continuity boundaries, and fail-closed lookup.
- `provenance/catalogs/` pins structural entity TSVs; `provenance/templates/` pins official PSD/QTO TSVs and exporter identity.

Never edit generated modules directly. Change the authoritative renderer or authenticated TSV source and regenerate the entire family. Never copy normative EXPRESS, PSD/QTO XML, or specification prose. Never substitute one IFC release for another or infer continuity from equal names/GUIDs. Official template rows remain distinct from corrected overlays.
