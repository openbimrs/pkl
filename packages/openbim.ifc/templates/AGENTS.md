# PSD/QTO release views

Generated, supported imports for official IFC template references.

- Choose exactly one edition module: `Ifc2x3.pkl`, `Ifc4.pkl`, or `Ifc4x3.pkl`.
- Use `propertySet`/`property` for PSD and `quantitySet`/`quantity` for QTO.
- Dynamic `*ByName` helpers fail closed on absent sets, wrong kinds, and invalid set/member pairs.
- Regenerate via `scripts/render-ifc-template-catalogs.py`; do not hand-edit generated `.pkl` files.
