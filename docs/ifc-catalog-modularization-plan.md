# IFC catalog modularization plan

## Goal

Replace the generated 8,787-line `packages/openbim.ifc/Catalog.pkl` compilation
unit with a small stable facade over generated internal data modules, without
changing the public resolver API or any release-specific result.

## Constraints

- Keep `Catalog.pkl`, `ifc.pkl`, and `versions/*.pkl` public behavior compatible.
- Keep IFC2X3 as the physical baseline and IFC4/IFC4X3 as explicit deltas.
- Do not copy normative EXPRESS or restricted specification prose.
- Generate every catalog data module from authenticated TSV inputs; do not hand-edit
  generated declarations.
- Keep `openbim.ifc@0.2.0` immutable. Publish the compatible refactor as `0.2.1`.
- Treat `internal/` as an unsupported package convention, not language-enforced
  privacy.

## Workstreams

1. Add a regression test that requires the intended generated file topology and
   caps the facade size.
2. Change `scripts/render-ifc-catalogs.py` to emit:
   - `Catalog.pkl`: releases, stable aliases, and resolver/evolution API;
   - `internal/Names.pkl`: closed entity-name union and runtime name list;
   - `internal/Ifc2x3Data.pkl`: physical baseline declarations;
   - `internal/Ifc4Data.pkl`: IFC4 delta and removals;
   - `internal/Ifc4x3Data.pkl`: IFC4X3 delta and removals;
   - `internal/Transitions.pkl`: observed snapshot transitions.
3. Update provenance completeness, mutation targets, package metadata, changelog,
   package docs, and progressive context.
4. Regenerate from authenticated TSV inputs and prove public behavior equivalence.
5. Build the package, independently review the exact commit/tree, publish 0.2.1,
   verify hosted resolution, then update MCS's checksum lock without changing rule
   semantics.

## Validation

- Run the topology test red before implementation, then green.
- `./scripts/gate.sh` and `python3 scripts/mutation-gate.py`.
- Compare public test output and release metrics with 0.2.0.
- Build the package with Pkl 0.32.1 and inspect ZIP topology/checksum.
- Evaluate a fresh remote consumer importing all three IFC versions and geometry.
- Run MCS's documented cold-cache `./scripts/check.sh` after lock-only adoption.

## Risks and rollback

- Qualified imported typealiases may not re-export as expected; validate with Pkl
  before broad generation changes.
- Mutation tests contain source-location assumptions and must move with data.
- Pkl package modules under `internal/` remain technically importable; documentation
  must disclaim their compatibility.
- Rollback is the immutable `openbim.ifc@0.2.0`; do not retag or replace its assets.

## Milestone status

- Topology test was observed RED against the 0.2.0 monolith and GREEN after
  generation of the five internal modules.
- The stable facade is 170 lines; the largest generated module is 3,154 lines.
- Full public storage evaluation produced byte-identical 232,091-byte JSON for
  0.2.0 and 0.2.1 candidate semantics, SHA-256
  `b51f6c2e2774032cabf39c53e1cdc0d7e8c8c77483bcad2771b4bd28defcc0d9`.
- The repository gate, deterministic provenance regeneration, eight mutation
  classes, and package construction pass with Pkl 0.32.1.

## Next action

Freeze the candidate commit, reconstruct it from an immutable archive, and obtain
an independent review before publishing 0.2.1.
