This module improves traceability in manufacturing by linking raw material
moves to their corresponding finished-product moves and by surfacing the
downstream deliveries directly on the manufacturing order.

- Links raw stock moves to finished-product moves so the full conversion path
  is visible in the stock traceability report.
- Adds computed fields on manufacturing orders to display the associated
  outgoing pickings and their moves.
- Exposes an optional "Stock Moves" smart button on the manufacturing order
  form view (visible to ERP managers) for quick access to all related moves.
- Adjusts list view columns for raw-material moves (name, BoM line, lock
  state) to show more relevant traceability data.
- Fixes a context-propagation issue in `stock.move.line._log_message` when
  a custom form view reference is active.

## Technical details

**Raw-to-finished move linking (`mrp.production`)**

`_update_raw_move_conv_dest_ids` is called on `create` and `write`. It writes
the finished-move IDs into the `move_conv_dest_ids` Many2many field on every
raw move of the production order. The inverse field `move_conv_orig_ids` on
`stock.move` then exposes the raw moves for a given finished move.

**Finished pickings computation (`mrp.production`)**

`_compute_finished_picking` walks the `move_dest_ids` chain recursively
starting from each finished move and collects all pickings encountered along
the way. The result is stored in `finished_picking_ids`,
`finished_picking_move_ids`, and `finished_picking_names`.

**`stock.move` extra fields**

Two symmetric Many2many fields (`move_conv_dest_ids` / `move_conv_orig_ids`)
are added to `stock.move` using a dedicated relation table
`stock_move_move_conv_rel`.

**`stock.move.line` log-message fix**

`_log_message` is overridden to strip the `default_state` key from the context
when the active form view is the custom stock-move details view, avoiding
side-effects on unrelated `state` fields (e.g. on `mail.tracking.email`).
