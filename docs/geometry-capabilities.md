# Geometry capability declarations

`openbim.geometry` is a vendor- and application-neutral vocabulary for answering a narrow question:

> Can this concrete geometry implementation satisfy this explicitly scoped geometric requirement?

It does **not** prescribe a CAD/BIM data model, file format, renderer, or a model-checking policy. An MCS rule should express its geometric prerequisites with `Requirements.pkl`; it must keep its domain verdict and rule semantics outside this package.

## Claim model

A manifest amends `schema/Manifest.pkl` and maps closed capability IDs to claims. Every claim supplies:

- a capability-contract version;
- `partial` or `full` support **only in the declared scope**;
- one or more quality guarantees;
- dimensions, input/output representations, and supported cases;
- limitations and at least one durable source/test/documentation/benchmark reference.

An absent key is **not implemented or not evidenced**. It is never inferred from an adjacent capability.

```pkl
amends "@geometry/schema/Manifest.pkl"

implementation {
  id = "org.example.kernel"
  name = "Example Kernel"
  version = "1.2.3"
}

capabilities {
  ["openbim.geometry:distance.minimum"] {
    version = "1"
    level = "full"
    exactness = List("exact-predicates")
    scope {
      dimensions = List("3D")
      inputRepresentations = List("triangle-mesh")
      outputRepresentations = List("point")
      supportedCases = List("Closed orientable triangle meshes.")
    }
    evidence = List(new {
      kind = "test"
      uri = "https://example.invalid/conformance/distance"
    })
  }
}
```

Consumers select the package alias they want (for example `geometry`) in their `PklProject`, so the neutral root can be imported exactly as `@geometry/schema/Manifest.pkl`.

## Quality is not a brand claim

`exactness` deliberately belongs to each claim, rather than to an implementation:

| Value | Meaning in the declared scope |
|---|---|
| `exact` | Exact constructions are retained/returned. |
| `exact-predicates` | Decisions are exact; constructed output may not be. |
| `analytic` | Analytic/parametric source definitions are retained; this is not symbolic-real arithmetic. |
| `topological` | The guarantee is structural/topological rather than metric. |
| `tolerance-bounded` | A stated algorithmic tolerance/error bound governs the result. |
| `conservative` | A positive result is safely conservative under the stated convention. |
| `approximate` | Sampling, floating point, or heuristic output without a stronger guarantee. |

`full` never means “works for all geometry.” It means the capability contract is complete for the stated dimensions, representations, and cases. `partial` records a known narrower implementation, even when the API works on common input.

## Catalog design

The catalog is separated so incompatible capabilities cannot be collapsed accidentally:

- `representation`: triangle/polygon mesh, analytic and NURBS curves/surfaces, B-rep/topological and set-theoretic solid forms;
- `query`: minimum/signed distance, directional clearance, containment, curve/surface intersection, and projection;
- `operation`: Boolean, construction, edit, and transform operations;
- `topology`: adjacency, manifold/geometric validation, tessellation, diagnosis, and explicit repair.

A capability ID is atomic. For example, `openbim.geometry:boolean.intersection` does not imply union/difference, and `openbim.geometry:intersection.surface-surface` does not imply curve/surface intersection or B-rep imprinting. Scope records whether an operation is 2D/3D, mesh/analytic/NURBS/B-rep, and what it returns.

## Requirements and conformance

`Requirements.pkl` describes what a downstream tool needs. A requirement includes the same quality and scope dimensions as a claim, with `allOf` and alternative `anyOf` profiles. `Conformance.pkl` is deliberately only the machine-readable report shape (`satisfied`, `unsatisfied`, or `indeterminate`). A checker performs matching outside Pkl so it can emit provenance, explain partial matches, and avoid importing MCS policy into the geometry vocabulary.

See `packages/openbim.geometry/examples/requirements/analytic-brep.pkl`: it requires both a trimmed analytic B-rep representation and geometric validation. A topology-only or mesh-only implementation cannot satisfy it by accident.

## Evidence basis for the initial catalog

The vocabulary was measured against different real kernel families, not invented from the Axiolid API alone:

- **Axiolid** distinguishes an analytic exact-B-rep *result contract* from its existing explicit mesh-generation and mesh-Boolean paths; unsupported exact construction/inversion is refused rather than silently tessellated. Its bundled manifest records only source-backed current claims.
- **CGAL** has configurable kernels: its [Kernel_23 documentation](https://doc.cgal.org/latest/Kernel_23/index.html) distinguishes exact predicates from exact constructions; [Nef_3](https://doc.cgal.org/latest/Nef_3/index.html) provides set-theoretic operations under its own representation/numeric assumptions; [Polygon Mesh Processing](https://doc.cgal.org/latest/Polygon_mesh_processing/index.html) has scoped mesh corefinement/Boolean operations. Therefore a future CGAL manifest must identify its selected kernel profile and operands rather than say “CGAL is exact.”
- **Open CASCADE Technology** documents oriented topological shapes in its [Modeling Data guide](https://dev.opencascade.org/doc/overview/html/occt_user_guides__modeling_data.html), B-rep operations and tolerance-aware algorithm families, and shape classification through [BRepClass3d](https://dev.opencascade.org/doc/refman/html/class_b_rep_class3d___solid_classifier.html). A future OCCT manifest should scope B-rep operations and tolerances; it must not equate a documented API with universal degeneracy robustness or exact arithmetic.

The catalog intentionally includes intersection, containment, distance, offset/fillet, repair, and set-theoretic representation IDs even when Axiolid does not currently claim them. This lets another kernel declare them precisely, while Axiolid’s absent claims remain an honest statement of current capability.
