This module automatically marks products as *favorites* (`favorite_ok`) when
they have already been used in the business. A 📌 pin emoji is appended to
the display name of favorite products so they can be quickly identified in
any dropdown or list.

A product is considered a favorite when it appears in at least one of:

- a sale order line
- a purchase order line
- a bill of materials as a component

## Technical details

**`favorite_ok` field**

A `Boolean` field added to `product.template`. It is set to `True` by the
`autoset_ok` scheduled action (inherited from `product_autoset_ok`) and
never reset automatically.

**Setting the flag**

`ProductTemplate.autoset_ok` is extended to call `_autoset_favorite_ok`
after the standard sale/purchase scan. `_set_attribute_ok` is also hooked
so that every time `sale_ok` or `purchase_ok` is activated for a batch of
products, those same products are also marked as favorites.
`_autoset_favorite_ok` reads all `mrp.bom.line` records and marks their
component products as favorites via `_set_favorite_ok`.

**Display name**

`_compute_display_name` is overridden on both `product.template` and
`product.product` to append the 📌 emoji when `favorite_ok` is `True`.
