# OpenBIM.rs Pkl packages

Pure [Apple Pkl](https://pkl-lang.org/) contracts for OpenBIM.rs standard families.
Each package is independently versioned and consumable through
[`Project.RemoteDependency`](https://pkl-lang.org/package-docs/pkl/current/Project/RemoteDependency.html).

## `openbim.loin`

`openbim.loin` transfers the complete public semantic model of the OpenBIM.rs
LOIN implementation into declarative Pkl:

- LOIN purpose, actor, milestone, object, alphanumerical, documentation,
  geometry, and georeferencing contracts;
- all closed wire vocabularies and ordered Purpose choice branches;
- lexical GUID, language, date-time, and email validation;
- non-empty and exact-cardinality constraints;
- a complete synthetic authoring example.

It is a semantic schema, **not an XML codec**. Apple Pkl does not consume XSD as
a native module, so the model is translated into Pkl classes and constrained
type aliases. No restricted ISO/CEN schema or standards text is vendored.

### Consume it remotely

In your `PklProject`:

```pkl
amends "pkl:Project"

dependencies {
  ["openbim.loin"] {
    uri = "package://openbimrs.github.io/pkl/openbim.loin@0.1.0"
  }
}
```

Then amend the schema root:

```pkl
amends "@openbim.loin/loin.pkl"

levelOfInformationNeed {
  specifications {
    new Specification {
      guid = "10000000-0000-0000-0000-000000000001"
      name = "Coordination"
      prerequisites = new Prerequisites {
        guid = "10000000-0000-0000-0000-000000000002"
        purpose = new Purpose {
          guid = "10000000-0000-0000-0000-000000000003"
          items {
            new PurposeName { value = module.multilingualText("en", "Coordination") }
          }
        }
        milestone = new InformationDeliveryMilestone {
          guid = "10000000-0000-0000-0000-000000000004"
          name = module.multilingualText("en", "Detailed design")
        }
        providingActor = new Actor {
          guid = "10000000-0000-0000-0000-000000000005"
          role = module.multilingualText("en", "Architect")
        }
        receivingActor = new Actor {
          guid = "10000000-0000-0000-0000-000000000006"
          role = module.multilingualText("en", "Engineer")
        }
      }
    }
  }
}
```

`pkl project resolve` records the selected package URI and checksum in
`PklProject.deps.json`. See `packages/openbim.loin/examples/basic.pkl` for a
complete configuration and `examples/consumer/` for the resolved and
gate-verified remote dependency.

### Develop

Requires Pkl 0.32.1 or newer:

```sh
scripts/gate.sh
pkl eval packages/openbim.loin/examples/basic.pkl
pkl project package --output-path build packages/openbim.loin
```

## `openbim.ifc`

`openbim.ifc` provides delta-compressed, release-explicit entity and official
PSD/QTO reference catalogs for IFC2X3 TC1, IFC4 ADD2 TC1, and IFC4X3 ADD2.
Stable entity and template facades compose generated baseline, delta, provenance,
and transition modules; thin version entry points reject names and set/member pairs
that are absent from the selected release. Canonical rows come from exact
`openbimrs/ifc` `ifc-schema` and `ifc-template-catalog` exports rather than
MCS-authored strings.

```pkl
import "@ifc/versions/Ifc4.pkl" as ifc4
import "@ifc/templates/Ifc4.pkl" as ifc4Templates

wall = ifc4.entity("IfcWall")
doorCommon = ifc4Templates.propertySet("Pset_DoorCommon")
handicapAccessible = ifc4Templates.property("Pset_DoorCommon", "HandicapAccessible")
netVolume = ifc4Templates.quantity("Qto_WallBaseQuantities", "NetVolume")
```

Template occurrences remain release-local. Same names and source GUIDs are
observations, not cross-release continuity claims; changed definitions receive
release-local revisions while unchanged semantics inherit from the nearest
snapshot. See [`docs/ifc-catalogs.md`](docs/ifc-catalogs.md) for counts,
provenance, capability limits, and the boundary with `openbim.geometry` and
Axioval MCS.

## `openbim.geometry`

`openbim.geometry` is a vendor- and application-neutral geometry-kernel capability
vocabulary. It keeps MCS/domain policy out of geometry declarations while letting
kernels publish evidence-backed, scoped support claims and downstream tools state
requirements. It covers representation, queries, Boolean/construction/editing,
topology, tessellation, and explicit repair without treating a mesh, B-rep, or
precision model as universal.

A claim is only meaningful with its declared dimensions, input/output
representations, supported cases, exactness/quality, limitations, and evidence.
CGAL, OCCT, and Axiolid therefore need not be flattened into the same purported
"exact geometry" capability.

```pkl
amends "@geometry/schema/Manifest.pkl"

implementation {
  id = "org.example.kernel"
  name = "Example Kernel"
  version = "1.2.3"
}
```

See [`docs/geometry-capabilities.md`](docs/geometry-capabilities.md), the
[Axiolid factual fixture](packages/openbim.geometry/conformance/axiolid.pkl),
and the [analytic B-rep requirement example](packages/openbim.geometry/examples/requirements/analytic-brep.pkl).

## Status

| Package | Version | Semantic model | XML codec |
|---|---:|---|---|
| `openbim.loin` | 0.1.0 | Implemented and tested | Not implemented |
| `openbim.ifc` | 0.3.0 | Delta-compressed entities plus official release-bound PSD/QTO references | Not applicable: schema-as-data |
| `openbim.geometry` | 0.1.0 | Implemented and tested | Not applicable: capability vocabulary |

See [`docs/loin-port.md`](docs/loin-port.md) for the audited port map and
capability boundary.

## License

Repository-authored work is `AGPL-3.0-or-later`. Historical MIT attribution
from the semantic source and buildingSMART CC BY-ND 4.0 attribution for
format-shifted IFC catalog facts are preserved; see [LICENSING.md](LICENSING.md),
package notices, and `LICENSES/`.
