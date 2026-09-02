# Generated IFC catalog internals

These modules are deterministic outputs of:

- `scripts/render-ifc-catalogs.py` for entity storage;
- `scripts/render-ifc-template-catalogs.py` for PSD/QTO storage.

Never edit them directly. Change the renderer or authenticated TSV inputs and regenerate the complete module family.

`Catalog.pkl`, `TemplateCatalog.pkl`, and the release modules under `versions/` are the supported public surfaces. Files here are packaged because those facades import them, but their paths and members carry no compatibility guarantee.
