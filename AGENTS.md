# Apple Pkl packages

This repository publishes independently versioned Apple Pkl packages for OpenBIM.rs standards.

- `packages/`: package projects; each child owns its `PklProject`, modules, tests, examples, and release version.
- `docs/`: repository-wide design and porting notes.
- `scripts/gate.sh`: local/CI verification entry point.

Do not vendor ISO/CEN schemas or restricted standards text. Public contracts must be derived from public implementation behavior and synthetic tests. Package consumers use `Project.RemoteDependency`; Pkl cannot interpret XSD as a Pkl module.
