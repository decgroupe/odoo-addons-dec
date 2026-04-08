This module adds delivery and task progression rate indicators to sale orders,
giving a quick overview of how far along a sale order is in its fulfilment.

- **Delivery rate**: overall fulfilment progress combining physical deliveries
  and service tasks into a single percentage shown in the list and form views.
- **Sent rate**: percentage of storable product lines whose ordered quantity has
  been fully delivered.
- **Task rate**: average progression of all project tasks linked to the sale
  order; closed tasks count as 100 % complete.
- **Delivery status per line**: each sale order line carries a computed
  `delivery_status` field (`Fully Delivered`, `To Deliver`, or
  `Nothing to Deliver`) that can be used for filtering and reporting.

## Technical details

**`SaleOrder._compute_sent_rate`**

Iterates over order lines whose product type is `consu` and counts how many
have `qty_delivered >= product_uom_qty`. The rate is `fully_delivered_lines /
total_consu_lines * 100`.

**`SaleOrder._compute_task_rate`**

Iterates over tasks linked to the sale order via `tasks_ids`. Tasks in a closed
state (`is_closed = True`) contribute 100 % to the total; open tasks contribute
their `progress` value (provided by `hr_timesheet`). The rate is the average
across all linked tasks.

**`SaleOrder._compute_delivery_rate`**

Combines `sent_rate` and `task_rate` depending on what the order contains:

- pickings only → `delivery_rate = sent_rate`
- tasks only → `delivery_rate = task_rate`
- both → `delivery_rate = sent_rate + task_rate / 2`
- neither → `delivery_rate = 100`

**`SaleOrderLine._compute_delivery_status`**

Computes a `Selection` field on each line:

- `none`: `product_uom_qty` is zero.
- `full`: `qty_delivered >= product_uom_qty`.
- `todo`: partially or not yet delivered.

Lines with a `display_type` (section/note) are excluded from the computation.
