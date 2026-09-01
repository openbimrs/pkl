# `openbim.loin`

Pure Apple Pkl semantic contracts for the public OpenBIM.rs LOIN model.

- `loin.pkl`: LOIN-owned vocabulary, classes, constraints, and authoring root.
- `iso23387.pkl`: explicitly partial imported-type boundary required by LOIN; not a complete `openbim.dt` package.
- `tests/loin.pkl`: behavior and constraint tests.
- `examples/basic.pkl`: complete synthetic authoring example exercising every LOIN branch.
- `PklProject`: package identity and release metadata.

The package models semantic authoring and validation. It does not parse or emit ISO XML and must not claim XSD round-trip parity.
