This module lets manufacturing users consume raw materials line by line from a
production order.

- Adds a dedicated Consume action on the manufacturing order form.
- Opens a wizard that computes required quantities from the entered production
	quantity and current BoM move factors.
- Lets users adjust consumed quantities per component before validation.
- Provides quick actions to minimize or maximize consumed quantities globally or
	per line.
- Keeps a traceable link between consumed raw-material move lines and finished
	product move lines.

## Technical details

**Production integration**

The module extends mrp.production and adds open_consume to launch the
mrp.consume wizard action. It also overrides _post_inventory to preserve
consume_line_ids links after inventory posting and adds
_post_inventory_consume(move_ids, cancel_backorder=False) to post only selected
raw moves.

**Consume wizard**

The transient model mrp.consume initializes defaults from the active
manufacturing order in default_get. The onchange on product_qty recomputes
line_ids from non-done raw moves using unit_factor and rounding by each move
UoM precision. On validation, do_consume applies entered quantities on moves,
marks them picked, posts selected moves, and switches the production state to
progress when needed.

**Wizard lines and UX helpers**

The transient model mrp.consume.line stores per-component quantities to consume,
reserved quantities, and entered consumed quantities. It computes button states
for minimize/maximize actions and provides per-line quick actions. The wizard
view defines bulk actions, make-to-order filtering, and visual warning
decorations when entered quantities exceed planned or reserved quantities.
