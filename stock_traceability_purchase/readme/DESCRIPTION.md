This module improves stock traceability for purchase-driven moves.

- it shows the purchase origin directly on stock moves.
- it keeps the purchase context visible even when links are later changed.
- it adds quick access to the related purchase document from traceability data.

## Technical details

**Purchase order display state**

It extends purchase orders with a computed `state_symbol` field to provide a
compact visual status used by traceability labels.

**Purchase line traceability label**

It overrides `purchase.order.line.get_head_desc` to return a purchase-specific
header and description built from the order number and current purchase state.

**Archive of created purchase links on stock moves**

It extends stock moves with `created_purchase_lines_archive` and archives the
purchase order reference when `created_purchase_line_ids` is set or modified,
so traceability can still show purchase context after link changes.

**Created items integration**

It extends `stock.move._get_mto_created_items` to add purchase records and the
purchase action (`action_view`) in the created-items payload for MTO or linked
purchase move flows.

**View extension**

It inherits the stock move form view from `stock_traceability` and injects
`created_purchase_line_ids` in the origin group.
