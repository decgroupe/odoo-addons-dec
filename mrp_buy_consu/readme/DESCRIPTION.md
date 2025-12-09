This module lets manufacturing teams choose, per BoM consumable line, whether
the component should be purchased or simply reserved from internal stock.

- Add a **Buy** option on BoM lines for consumable products.
- Keep the default consumable flow when **Buy** is not enabled.
- Show procurement method on manufacturing raw moves to make the behavior clear.

## Technical details

**BoM line flag and UI**

The module extends `mrp.bom.line` with a `buy_consumable` boolean and related
helper fields linked to the product consumable status. It injects the
`buy_consumable` field into both the BoM form line list and the BoM line form.
In the BoM line list, the field is visible only when the product is consumable.

**Procurement behavior override**

`stock.move._adjust_procure_method()` is overridden to force
`procure_method = "make_to_order"` for moves linked to consumable BoM lines
where `buy_consumable` is enabled, so replenishment is done through purchase.
All other moves keep the standard behavior by delegating to `super()`.

**Location behavior for non-bought consumables**

`stock.move._compute_location_id()` is overridden for consumable BoM moves
without `buy_consumable` to keep source and destination locations aligned with
the production destination location, while preserving standard computation for
all other moves.

**Manufacturing view enhancement**

The manufacturing order form raw moves list is extended to show
`procure_method` (restricted to advanced location users), helping users verify
whether a consumable line will be bought or consumed from stock.
