This module links sale orders to their procurement groups, making it easy to
trace which sale orders triggered a procurement and navigate between them.

- Adds a **Sales** smart button on procurement group forms showing the number of
  linked sale orders and opening them in one click.
- Adds a **Sale Orders** tab on the procurement group form listing all orders
  associated with the group.
- Shows the **Procurement Group** field on the sale order form so users can see
  which group a sale order belongs to.
- Extends the procurement group list view with the linked sale order reference.

## Technical details

**New fields on `procurement.group`**

- `sale_order_ids` (`One2many` → `sale.order`, inverse of `procurement_group_id`):
  all sale orders that share this procurement group.
- `sale_order_count` (computed `Integer`): number of linked sale orders,
  used by the stat button.

**`action_view_sale_orders`**

Calls `sale.order.action_view()` (provided by `sale_action_view`) and narrows
the domain to `procurement_group_id = self.id`. Returns the resulting action
dict so the stat button opens the correct records.

**View extensions**

- `procurement_traceability.procurement_group_form_view`: adds the stat button,
  the Sale Orders tab, and the `sale_id` field in the General group.
- `procurement_traceability.procurement_group_tree_view` (list): adds the
  `sale_id` column after `move_type`.
- `sale.view_order_form`: adds `procurement_group_id` after the `origin` field.
