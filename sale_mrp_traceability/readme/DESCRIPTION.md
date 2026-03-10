This module links sale order traceability with manufacturing traceability by
displaying related stock moves (including manufacturing-generated moves) directly
on the sale order line form.

- Adds a **Stock Moves** block inside the traceability section of each sale
  order line, visible only to users with the *Manufacturing Traceability* group.
- Each move shows its product, unit of measure, status, and procurement status,
  with a quick-access button to open the linked procurement document.

## Technical details

**Sale order form extension**

Inherits `sale_traceability.sale_order_form_view` to inject a
`<div name="moves">` inside the `traceability_container` div. The div is
restricted to users in `group_sale_mrp_traceability` and hidden when there are
no moves or when the line has a display type (section/note).

**Custom stock move list view**

Provides a dedicated list view (`stock_move_tree_view`) for `stock.move` used
as the embedded widget in the sale order line form. It displays the procurement
status field (`pick_status`) from `mrp_traceability` and a button to open the
linked procurement document (`action_view_created_item`).
