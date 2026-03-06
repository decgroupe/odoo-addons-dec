This module improves the component consumption wizard in Manufacturing by
showing where each product is physically stored and by letting users request an
inventory check directly from a consume line.

- Displays a Location column on consume lines using product rack/row/case data.
- Adds a button to create an inventory activity for the selected product.
- Reopens the consume wizard after activity creation so the user can continue
	the operation.

## Technical details

**Location display on consume lines**

The module extends the transient model `mrp.consume.line` and adds a computed
char field `product_location`. The compute method builds the display value from
`product_id.loc_rack`, `product_id.loc_row`, and `product_id.loc_case`, joined
with the visual separator used by the module.

**Wizard view extension**

The inherited view `mrp_production_consume.mrp_consume_wizard_view` inserts the
`product_location` field in the list of consume lines and adds a button on each
line to trigger inventory activity creation.

**Inventory activity creation**

The `action_create_inventory_activity` method creates a `mail.activity` on the
related `product.template` record with the summary "Requires inventory". When
the line is attached to a consume wizard, the wizard is reopened via `_reopen()`
to preserve the user workflow.
