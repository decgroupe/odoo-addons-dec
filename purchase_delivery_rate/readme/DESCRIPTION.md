This module adds a **delivery rate** indicator to purchase orders, showing the
percentage of ordered products that have been fully received.

- The `picked_rate` field is displayed as a progress bar in the purchase order
  list and form views, visible only when the order is in state *Purchase Order*,
  *Done*, or *Cancelled*.
- Only storable and consumable product lines are counted; service lines are
  excluded from the computation.

## Technical details

**`picked_rate` field on `purchase.order`**

A stored `Float` field computed by `_compute_picked_rate`, triggered whenever
`state`, `order_line.qty_received`, or `order_line.product_qty` changes. For
each non-service order line with a positive ordered quantity, the method checks
whether `qty_received >= product_qty` (using `decimal.precision` for
comparison). The rate is expressed as `(fully_received_lines / total_lines) *
100`.

`action_update_picked_rate` is a public method provided for manual
recomputation (e.g. from a button action).

**Views**

The `picked_rate` progress bar is injected into:

- `purchase.purchase_order_tree` (main list view)
- `purchase.purchase_order_view_tree` (alternative list view)
- `purchase_stock.purchase_order_view_form_inherit` (form view, after the
  vendor reference field)

