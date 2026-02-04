This module adds a last delivery date overview on sales orders.

- Shows the latest expected delivery date across all non-delivery order lines.
- Shows the latest effective delivery completion date based on delivered lines.
- Helps sales users communicate the final delivery horizon for partially delivered orders.

## Technical details

**Latest expected delivery date**

The module extends `sale.order` with a computed `expected_last_date` field. It
collects expected dates from each relevant order line and keeps the maximum
value as the final expected delivery date.

**Latest effective delivery date**

The module extends `sale.order` with a stored computed `effective_last_date`
field. It aggregates `last_effective_date` values from order lines and stores
the latest one on the order.

**Form view integration**

The inherited sale order form inserts these two fields around the existing
effective date field. The expected-last-date field is hidden when the order uses
the "deliver all at once" policy (`picking_policy == 'one'`).
