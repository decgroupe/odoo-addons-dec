This module improves traceability on purchase order lines by showing where each
line comes from in the replenishment chain.

- Displays origin information directly on purchase lines (orderpoint,
	manufacturing order, sales flow, procurement group, and related picking).
- Adds a quick action to jump to the most relevant origin document from the
	purchase line.
- Propagates procurement group information when needed so links remain
	consistent.

## Technical details

**Purchase order processing hooks**

The module extends `stock.rule._run_buy` to set a context flag used during the
buy flow. It then extends `purchase.order.create` and `purchase.order.search` to
trigger `_buy_postprocess()` when the flow is initiated from `_run_buy`, and can
post contextual messages using context keys. It also extends `purchase.order.write`
to propagate `group_id` to lines missing `procurement_group_id`.

**Purchase line origin computation**

The module extends `purchase.order.line` with computed helper fields that build a
consolidated origin payload from `move_dest_ids`, `orderpoint_ids`,
`procurement_group_id`, related productions, sales lines/orders, and pickings.
This payload is formatted as HTML for display in the purchase line and used to
control visibility of the origin action button.

**Navigation to origin records**

The method `action_view_origin_item` selects the best available origin in
priority order (orderpoint, production, sales order, procurement group) and
delegates navigation through the corresponding `action_view()` implementation.
