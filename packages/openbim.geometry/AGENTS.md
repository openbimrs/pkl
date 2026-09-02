# `openbim.geometry`

Application- and vendor-neutral Pkl vocabulary for declaring **geometry kernel capabilities**, requirements, and externally computed conformance reports.

- `schema/`: shared manifest, requirement, quality, and report types.
- `capabilities/`: closed, versioned atomic capability IDs.
- `conformance/`: factual implementation manifests; claims require scope, limitations, and evidence.
- `examples/`: neutral downstream requirement profiles.
- `tests/`: Pkl schema and manifest validation.

This is not a CAD/BIM object model, mesh format, B-rep exchange format, or a model-checking policy language. Never add vendor names or application verdicts to the shared catalog. Split a capability before claiming a broad operation across incompatible representations or guarantees.
