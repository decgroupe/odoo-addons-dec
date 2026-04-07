This module adds a smart button on the purchase order form that shows the
outgoing delivery orders (shipments) waiting for the purchased goods.

- **Outgoing pickings button**: displays a count badge on the purchase order
  form with a link to all delivery orders whose moves are linked to the
  purchase order lines via `move_dest_ids`. Only visible when at least one
  outgoing picking exists.

## Technical details

**Outgoing pickings button**

Extends `purchase.order` with two computed fields:

- `outgoing_picking_ids` (`One2many` → `stock.picking`): collects all pickings
  reachable via `order_line.move_dest_ids.picking_id` and removes the
  purchase's own receipt pickings (`picking_ids`) from the result.
- `outgoing_picking_count` (`Integer`): the number of outgoing pickings, used
  by the stat button widget.

Both fields depend on `order_line.move_dest_ids` and `picking_ids` so they are
automatically recomputed whenever these change.

The `action_view_outgoing_picking` method mirrors the behaviour of the built-in
`action_view_picking`: it opens the form view directly when only one outgoing
picking exists, and switches to a list view filtered by domain when there are
several.
