When a manufacturing order is unbuilt, the components that are returned to stock
may no longer need to follow a Make To Order (MTO) replenishment strategy. This
module automatically adjusts their replenishment route so that the stock is
correctly managed after the return.

- When components are returned to stock via an unbuild order, any component
  whose product template carries the **MTO** route has that route replaced with
  the **MTO + MTS** (Make To Order + Make To Stock) route.
- A chatter message is posted on each affected product template listing the
  route change.
- A chatter message is posted on the unbuild order listing all products whose
  routes were edited.

## Technical details

- Overrides `mrp.unbuild._generate_produce_moves` to call
  `product.product.update_routes_after_return_to_stock` on every component
  product involved in the produce moves. If any routes were changed, a
  formatted HTML message is posted on the unbuild record via `message_post`.
- Adds `product.product.update_routes_after_return_to_stock(reason)` which
  iterates over the product templates of the given products: if the MTO route
  is present but MTO+MTS is not, it swaps them and posts a message on the
  product template.
- Produce moves generated during the unbuild have their `move_orig_ids` set to
  the unbuild's `consume_line_ids` for traceability.
- Depends on `product_legacy_routes` for the `_get_mto_route` and
  `_get_mto_mts_route` helpers, and on `stock_mts_mto_rule` for the MTO+MTS
  route.
