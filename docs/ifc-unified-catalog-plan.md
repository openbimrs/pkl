# Unified IFC evolution catalog plan

Status: active design and implementation

## Goal

Replace three generated full-release Pkl snapshots with one canonical evolution catalog. Keep every public result release-bound and fail closed when a name does not exist in the selected release. Use the same revision model later for PSD/QTO templates and members.

## Evidence

Frozen structural exports contain 2,305 entity rows but only 1,006 union names and 1,236 distinct direct-declaration revisions after factoring each entity to its immediate supertype plus directly declared attributes. Exact revision sharing removes 1,069 repeated expanded rows before direct-declaration normalization. Presence across the supported releases is non-monotonic: 533 names occur in all three releases, 6 only in IFC2X3+IFC4, 227 only in IFC4+IFC4X3, and 240 in one release only.

Between IFC2X3 and IFC4 there are 237 observed additions, 114 observed removals, and 162 changed shared direct declarations. Between IFC4 and IFC4X3 there are 116 additions, 16 removals, and 68 changed shared direct declarations. These are supported-snapshot differences, not claims about the exact historical introduction/removal release.

The official IFC4 Annex F changelogs explicitly classify additions, modifications, deprecations, and removals. Changelog evidence must be recorded separately from inferred snapshot differences. The authenticated source corpus now covers IFC2X3 PSD XML, IFC4 ADD2 TC1 PSD/QTO XML, and IFC4X3 ADD2 PSD/QTO XML at the pinned buildingSMART release commit.

A 30-sample alternated warm process benchmark on Pkl 0.32.1 evaluated the
same cross-release `IfcWall` release, ancestry, and inherited-attribute output.
The `0.1.0` baseline median was 66.835 ms (Q1-Q3 64.595-68.122 ms);
`0.2.0` was 29.493 ms (28.885-31.232 ms), a 55.9% reduction for this
workload. Both emitted the same 754 bytes, SHA-256
`039dda777e6fc088badf242c05aec212cfdd854806da62de56045fffc2b26aa5`.
The deterministic package ZIP fell from 89,126 to 58,509 bytes (34.4%);
its uncompressed payload fell from 952,693 to 340,312 bytes (64.3%).

## Contract

1. One union `EntityName` type catches unknown spellings once.
2. `EntityEvolution` owns exact direct declarations keyed by every supported `ReleaseId` in which the entity is present.
3. A resolver accepts `(release, name)` and returns a release-bound `EntityReference`, or fails if no exactly-one revision applies.
4. Thin `versions/Ifc2x3.pkl`, `Ifc4.pkl`, and `Ifc4x3.pkl` modules preserve convenient version-specific imports while delegating to the unified catalog.
5. Storage deduplication is never semantic collapse: every resolved reference retains its exact release and external type-system identity.
6. Lifecycle evidence distinguishes:
   - exact supported-snapshot membership through `definitions` keys;
   - derived `observedAddedIn` / `observedRemovedIn` transitions;
   - proven `introducedIn`, `deprecatedIn`, `removedIn`, `renamedTo`, or `replacedBy` only when an official changelog states it.
7. Pkl reflection can read annotations on static declarations, but IFC entities are release-indexed catalog values. Typed lifecycle data is canonical; annotations may only mirror it on static facade members.
8. Canonical `ifc-schema` exports direct declarations; Pkl resolves ancestry and inherited Part 21 attributes per release instead of repeating inherited rows.

## PSD/QTO extension

Use parallel versioned data, not free-form property strings:

- `TemplateOccurrence`: an exact `(release, kind, source name)` PSD/QTO record with
  optional source GUID, applicability clauses, template type, source path, and
  source digest.
- `MemberOccurrence`: an exact nested member path inside one occurrence, with
  optional source GUID and property/quantity kind, value type, unit,
  enumeration, and source evidence. Published QTO members have no member GUID;
  absence stays explicit.
- `TemplateEvolution`: only groups occurrences connected by explicit
  `ContinuityEvidence`. A shared name or GUID can produce a candidate match but
  never establishes cross-release identity by itself.
- `CandidateContinuity`: release-pair observations such as same name, same GUID,
  changed GUID, or changed kind. They remain non-normative until accepted with
  authenticated evidence.
- Lifecycle evidence follows the structural model: exact occurrence membership,
  observed transitions for an explicitly tracked identity, and separately
  sourced normative introduction/deprecation/removal/rename claims.
- Applicability and member changes are revisions, not silent patches.
- Official snapshots and corrected/advisory profiles remain distinct, following
  `ifc-template-catalog`'s immutable snapshot and overlay model.

The canonical Rust `ifc-template-catalog` owns XML interpretation and exports
release-explicit deterministic TSV. Its contract includes edition, set kind and
name, optional set/member GUIDs, exact applicability, nested member path, member
kind/value/unit, source digest, source path, and per-file digest. The Pkl package
must consume that export; it must not independently parse or copy official XML.
MCS consumes package-owned references and must not own an IFC template schema.

## Template evidence measured

Release snapshots contain 317, 513, and 612 templates and 3,019, 3,525,
and 4,361 deterministic TSV rows. IFC2X3's authenticated snapshot has no
standardized QTO XML. The three-release name union has 700 candidates; IFC4 to
IFC4X3 has 503 shared names, 109 additions, and 10 removals. These name matches
are candidate continuity observations only. `Pset_Risk`, for example, has a
different published set GUID in IFC4 and IFC4X3 despite retaining its name.

The IFC4X3 ADD2 template source is pinned at buildingSMART
`IFC4.x-development` commit
`524daac53ca682e0649d240ace87f4cd7baff6e7`, tree
`5ac02c6686df303a49e9bf5c05c75a0c91240aa7`.

Snapshot diffs stay separate from normative changelog evidence. Pkl annotations attach to static declarations, while lifecycle status varies by release on runtime catalog values; explicit release-indexed values remain authoritative.

`openbim.ifc@0.2.0` remains structural-only. The template export and evolution
contract are now explicit, but shipping the multi-megabyte PSD/QTO runtime data
is deferred to a later reviewed package revision. That revision must measure
archive/evaluation cost and resolve continuity evidence without weakening the
release-local occurrence model.

## Workstreams

1. Add deterministic unified structural export/rendering with exact revision grouping.
2. Build the unified Pkl resolver and thin release modules under a breaking package version.
3. Prove all prior release counts, ancestry, attributes, non-existence cases, and release identity.
4. Land the canonical Rust template exporter across all three authenticated snapshots and freeze the occurrence/evidence contract before later Pkl ingestion.
5. Update MCS adapters without changing normalized MCS meaning. Canonical external IFC identifiers must remain stable; package transport URIs must not masquerade as domain type-system identities.
6. Enforce project alias/lock consistency during MCS archive creation and use a fresh package cache for pack-time checksum verification. Offline archive verification authenticates archived lock bytes but must not claim to revalidate remote metadata.

## Validation

- Deterministic regeneration and source/hash drift gates.
- Mutation tests for release membership, one revision shape, lifecycle evidence, and resolver fail-closed behavior.
- Size/row comparison against the three-snapshot package.
- `pkl test` across all release wrappers and representative changed/removed entities.
- PSD/QTO export tests for exact release inventories, release-scoped GUIDs,
  `Pset_Risk`'s changed-GUID candidate, and IFC2X3's explicit absence of QTO XML.
- Fresh-cache remote package resolution and MCS pack/eval.
- Immutable archive review, release checksums, hosted package metadata, CI, and canonical-checkout verification.

## Risks and rollback

- A unified internal model can accidentally erase release identity. The public resolver must always return `release` and tests must mutate it.
- Snapshot diffs do not prove deprecation or rename. Keep observed transitions separate from normative lifecycle evidence.
- This is a breaking package API change; publish a new package version and retain immutable `0.1.0`.
- Do not modify shared checkouts. Land exporter, package, and MCS changes through isolated reviewed candidates.
