This module lets buyers remove a purchase order line with two options depending
on the expected downstream impact.

- Delete only the purchase line when you do not want to cancel the linked
	downstream flow.
- Delete the purchase line and propagate cancellation to linked stock moves when
	the procurement chain must be stopped.
- Keep business documents consistent by updating related moves and cancelling
	purchase orders that become empty after line deletion.

## Technical details

**Purchase line cancellation actions**

The module extends purchase order lines and adds two object actions from the
purchase order line list inside the purchase order form. The action method
`action_propagate_cancel` reads a `propagate` flag from context, posts a
chatter message on the purchase order, unlinks the selected line, and cancels
the purchase order if it has no remaining lines.

**Downstream stock behavior**

If propagation is enabled, destination moves are cancelled through downstream
cancellation calls. If propagation is disabled, the line forces
`propagate_cancel = False` before deletion so Odoo keeps the downstream flow
and switches impacted destination moves to `make_to_stock` when required.

**Move owner notifications and data consistency**

Before unlinking move links, the module computes notifications for impacted move
owners (for example pickings) and posts a summary in chatter. During unlink, it
detaches destination move links and updates procurement-related fields to avoid
inconsistent move chains.
