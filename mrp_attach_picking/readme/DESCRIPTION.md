This module lets you attach a manufacturing order to an existing delivery
picking when the production was not originally linked to one.

- It adds an action on the manufacturing order form to select an existing
	delivery move.
- It helps connect manually created production orders to outgoing delivery
	flows.
- It is useful when logistics planning requires linking production output to a
	specific customer delivery.

## Technical details

**Manufacturing order form extension**

The module extends `mrp.production` with a computed boolean field
`allow_attach_picking`. This field is true only when finished moves are not yet
linked to downstream destination moves. The manufacturing order form view is
inherited to display an "Attach to picking" group and action button only when
that field allows it.

**Attach wizard**

The transient model `mrp.attach.picking` is opened by the form action. Its
defaults are filled from the active `mrp.production` record. The selectable
`stock.move` is constrained in the view domain to match product, quantity,
outgoing destination usage, no existing origin links, `make_to_stock` procure
method, and states `confirmed` or `assigned`.

**Link operation**

On confirmation (`do_attach`), the wizard filters production finished moves to
usable states, switches the selected move to `make_to_order`, recomputes state,
links finished moves as origins, recomputes state again, and triggers
assignment. If no eligible finished move exists, it raises a validation error.
