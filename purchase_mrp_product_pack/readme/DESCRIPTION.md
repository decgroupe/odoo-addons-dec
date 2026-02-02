This module makes purchase flows work correctly when purchased products are
packs used by manufacturing.

- It creates stock moves for each pack component when incoming pickings are
	generated from purchase orders.
- It keeps move sequencing consistent for manufacturing raw material moves,
	including nested pack components.
- It automatically marks parent pack moves as done when only component products
	are physically received.
- It propagates the procurement group and formats child line labels in purchase
	order pack lines.
- It prevents deleting protected child pack lines directly and shows an explicit
	error message when this is not allowed.

## Technical details

**Purchase picking and pack move creation**

`purchase.order` overrides `_create_picking()` to create pack child stock moves
before standard picking creation and to force parent pack moves done afterward.
It also collects related `mrp.production` records and refreshes raw move
sequences.

**Pack purchase order line lifecycle**

`purchase.order.line` extends unlink behavior to remove child lines safely,
cancel and delete linked destination moves when needed, enforce pack line delete
rules, and build child move values from parent move data.

**Stock move hierarchy and sequencing**

`stock.move` adds `pack_parent_move_id`, `pack_child_move_ids`, and computed
`pack_level`, then overrides `_update_sequence()` to handle recursive sequence
updates across pack move trees while avoiding duplicate updates.

**MRP raw move ordering**

`mrp.production` adds `update_move_raw_sequences()` to sort raw moves and apply
the custom stock move sequence update.

**Pack line purchase values**

`product.pack.line` overrides `get_purchase_order_line_vals()` to inject
`procurement_group_id` from the purchase order and prefix generated line names
according to pack depth.
