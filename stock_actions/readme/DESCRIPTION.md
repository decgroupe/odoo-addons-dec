This module adds operational action buttons on stock moves directly from picking
operations.

- Reassign: unreserves the move and recomputes availability.
- Set Make to Order: switches eligible moves from make-to-stock to
	make-to-order and confirms them again.
- Cancel: cancels eligible moves from the operation view.
- Done: validates eligible moves and pickings from the action flow.

## Technical details

**Stock move actions and visibility**

The module extends stock.move with computed technical booleans used by the list
view buttons:
- action_reassign_visible is computed by
	_compute_action_reassign_visible() based on reservation, lock status, and
	state.
- action_set_mto_visible is computed by _compute_action_set_mto_visible() based
	on quantity, lock status, state, and procure_method.
- is_cancellable is computed by _compute_is_cancellable() according to
	procure_method and state.

**Action methods on stock.move**

The module adds object methods to trigger workflow transitions from the UI:
- action_confirm() and action_assign() wrap internal stock workflows.
- action_reassign() performs _do_unreserve() then _action_assign().
- action_set_mto() unreserves, writes state/procure_method, then calls
	_action_confirm().
- action_cancel(), action_cancel_downstream(), and action_cancel_upstream()
	route to _action_cancel_stream(), which recursively collects related moves
	through move_orig_ids and move_dest_ids for the same product.
- action_done() sets picked and calls _action_done().

The write() override logs state and procure_method changes for traceability.

**UI integration**

The module inherits stock.view_picking_form and injects object buttons inside
the move_ids_without_package list (after lot_ids), using invisible and
column_invisible modifiers on technical booleans.

**Picking completion helper**

The stock.picking action_done() override only processes pickings in actionable
states and calls _action_done() for them.
