This module lets you merge multiple purchase quotations into a single purchase
order.

- merge selected quotations from the purchase order list view.
- keep one selected quotation or create a new target quotation.
- optionally merge similar lines by adding quantities.
- choose what happens to source quotations after merge (cancel or delete).

## Technical details

**Mergeable states extension**

The module extends `purchase.order` and overrides `_get_mergeable_states()` to
authorize merging for orders in `draft`, `sent`, and `to approve` states.

**Merge wizard and validations**

The transient model `purchase.order.merge` validates the selection before merge:
minimum number of orders, compatible states, and a single vendor across all
selected orders.

**Line merge logic**

When line quantity merge is enabled, lines are merged only when product, unit
of measure, unit price, procurement group, taxes, and description all match.
Otherwise lines are moved as-is to the target order with sequence recomputation.

**Traceability and post-processing**

The wizard updates the target `origin`, posts chatter messages using
`message_post_with_source()` and QWeb templates (`merged_with_template`,
`merged_to_template`), then post-processes source orders by canceling or
deleting them according to wizard options.
