This module adds action buttons to the raw material moves list inside a
manufacturing order, enabling quick stock management operations directly from
the production form.

- **Re-check availability**: unreserves the move and immediately re-checks
  availability, useful when stock has changed since the last reservation.
- **Change procure method to Make to Order**: switches the move's procurement
  method from *Make to Stock* to *Make to Order* and triggers a new restock
  order (purchase or sub-manufacture). Only available when the move has no
  reserved quantity yet.
- **Cancel**: cancels the individual raw material move without cancelling the
  whole manufacturing order. Only available for moves that are not yet done or
  already cancelled.

All three buttons are hidden when the manufacturing order is locked.

## Technical details

**Re-check availability button** (`action_reassign`)

Rendered via a computed Boolean field `action_reassign_visible` on
`stock.move` (provided by the `stock_actions` module). The button is visible
when the move has not been fully reserved, is not locked, and its state is in
`confirmed`, `waiting`, `partially_available` or `assigned`.

**Change to MTO button** (`action_set_mto`)

Rendered via `action_set_mto_visible`, also computed on `stock.move`. The
button is visible only when the move has zero reserved quantity, is in *Make to
Stock* mode, and has a state allowing procurement (draft through assigned).
Clicking it unreserves the move, sets `procure_method` to `make_to_order`, and
runs `_action_confirm` to trigger the appropriate restock rule.

**Cancel button** (`action_cancel`)

Visibility is controlled by the computed Boolean `is_cancellable` on
`stock.move`. The column itself is hidden (`column_invisible`) when the
manufacturing order is locked (`parent.is_locked`). The method
`action_cancel` delegates to `_action_cancel_stream` which cancels the move
and any dependent moves in the chain.
