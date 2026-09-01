# `openbim.loin` port map

## Provenance

The canonical source was audited at OpenBIM.rs LOIN revision
`07e486aae96346caa7eb796c2238479d1ca6cd2f`. Its semantic implementation files
are unchanged from `7f81f96084f89e00aed9e08792428074a0535423`; the later commits adopt
`AGPL-3.0-or-later` while preserving the prior MIT terms in `LICENSES/MIT.txt`.
The source repository contains no tracked XSD, ISO/CEN annex, restricted
reference material, or real standards fixture. Public fixtures are synthetic.

The Pkl package does not copy standards text. It expresses the public model and
observable validation contracts in native Apple Pkl.

## LOIN-owned model coverage

| Rust/public concept | Pkl contract |
|---|---|
| `LevelOfInformationNeed`, `Specification` | `LevelOfInformationNeed`, `Specification`, root `levelOfInformationNeed` |
| `Purpose`, all seven ordered `PurposeItem` branches | `Purpose` plus seven `Purpose*` subclasses |
| `Actor`, `InformationDeliveryMilestone`, `Prerequisites` | same-named classes |
| `SpecificationPerObjectType` | same-named class |
| `AlphanumericalInformation`, `GroupsOfProperties` | same-named classes |
| `Documentation`, `Document`, `DocumentFormat` | same-named classes |
| `GeometricalInformation`, `Detail`, `ShapeInfluence`, `ThresholdDimension`, `Location` | same-named classes |
| geometry option vocabularies | closed literal-union type aliases |
| `GeoReferencing`, `CoordinateReferenceSystem`, `Datum`, `DatumRegistryReference`, `ModelCoordinateSystem` | same-named classes |
| constructors rejecting empty Purpose/email errors | invalid states rejected through Pkl constrained types |
| enum `as_str` behavior | literal values are the wire spellings |

Public field names use idiomatic Pkl `camelCase` equivalents of Rust
`snake_case` names. Listing order is retained, including the repeating Purpose
choice.

## Imported ISO 23387 boundary

LOIN imports concept, object type, property, quantity kind, property group,
reference document, dimension, unit, reference, and primitive value contracts
from ISO 23387. `iso23387.pkl` models exactly the surface consumed by LOIN and is
explicitly extensible. It is **not** presented as complete ISO 23387 support.

A future independently released `openbim.dt` package can replace this local
boundary through a `Project.RemoteDependency`. That migration must preserve the
LOIN field contract and receive compatibility tests before release.

## Validation represented natively

- GUID lexical form.
- XML-language lexical form.
- XML-date-time lexical form used by the public value layer.
- LOIN email-address acceptance contract.
- Closed geometry and CRS wire vocabularies.
- Non-empty root specification, Purpose, document-format name/version,
  concept-name, property-reference, and language listings.
- Exactly seven SI base-dimension exponents.
- Required fields represented as non-null Pkl properties.

## Executable mutation evidence

The `2026-09-01` verification deliberately injected and restored six semantic
mutations. The test suite rejected all six, and source hashes matched after
restoration:

| Mutation | Result |
|---|---|
| accept every GUID | rejected |
| allow an empty root `specifications` listing | rejected |
| allow an empty `Purpose.items` listing | rejected |
| allow an empty document-format `versions` listing | rejected |
| remove `ProjectedCRS` from the closed vocabulary | rejected |
| accept 29 February in a non-leap year | rejected |

A final unchanged run passed after restoration.

## Deliberate capability boundary

Implemented:

- declarative authoring;
- model evaluation and rendering through Pkl renderers;
- native schema/type/cardinality validation;
- stable package and remote-dependency contracts.

Not implemented:

- XSD loading or code generation;
- LOIN XML parsing or serialization;
- automatic XML Schema whitespace collapsing or `anyURI` escaping (authored
  Pkl values must already be normalized);
- namespace-based document parsing;
- source line/column XML diagnostics;
- byte-for-byte or lossless XML round trips.

Those are codec capabilities and must not be inferred from semantic model
coverage.
