# `openbimrs/pkl`

Pure Apple Pkl packages for OpenBIM.rs standard-family contracts.

## Commands

```sh
scripts/gate.sh
pkl project package --output-path build packages/openbim.loin
```

## Conventions

- One independently versioned package project per `packages/<display-name>/`.
- Package display names use `openbim.<family>`.
- Public modules contain declarative contracts and validation; examples are synthetic.
- Never vendor restricted ISO/CEN schemas or text.
- Keep capability claims honest: model/schema parity is distinct from XML codec parity.
- Update `CHANGELOG.md` and package port documentation for public API changes.
