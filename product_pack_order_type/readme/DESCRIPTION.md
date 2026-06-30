This module lets you control where a product pack is expanded.

- All: the pack is expanded on both sale and purchase orders.
- Sale: the pack is expanded only on sale orders.
- Purchase: the pack is expanded only on purchase orders.
- Pack lines are also duplicated when a packed product template is copied.

## Technical details

**Order type on product templates**

The module adds a `pack_order_type` selection field on `product.template` with
`all`, `sale`, and `purchase` values.

**Conditional pack expansion**

It extends `sale.order.line.expand_pack_line` and
`purchase.order.line.expand_pack_line` to call the parent expansion only when
the product is a pack (`pack_ok`) and the selected order type matches the
current document.

**Template copy behavior**

It overrides `product.template.copy` to duplicate `pack_line_ids` manually and
relink them to the new variant through `parent_product_id`.
