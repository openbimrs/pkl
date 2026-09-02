# Generated IFC catalog internals

These modules are deterministic outputs of `scripts/render-ifc-catalogs.py`.
Never edit them directly; change the renderer or authenticated structural TSV
inputs and regenerate the complete set.

`Catalog.pkl` is the only supported public catalog surface. Files here are
packaged because the facade imports them, but their paths and members carry no
compatibility guarantee.
