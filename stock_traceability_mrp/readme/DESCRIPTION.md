This module extends stock traceability for manufacturing flows.

- Adds a procurement status column on manufacturing component moves to show the
	upstream MRP status directly from the production order.
- Adds a quick "Open" action on component lines to open the related created
	manufacturing document.
- Displays manufacturing origin links on stock moves (`created_production_id`,
	`production_id`, `raw_material_production_id`) to simplify traceability.
- Preserves historical references to created manufacturing orders in the status
	display, including canceled flows.

## Technical details

**Stock move extensions**

The module extends `stock.move` by adding a computed HTML field `mrp_status`,
archiving created production references in `created_productions_archive`, and
adapting status computation to include MRP-specific cases. It also extends
created-item resolution so manufacturing orders can be opened from traceability
status actions.

**Manufacturing order extension**

The module extends `mrp.production` with a computed `state_symbol` used by the
traceability header, and overrides `write()` to archive created production
references when destination moves are updated.

**View integration**

The inherited manufacturing form view (`mrp.mrp_production_form_view`) adds the
`mrp_status` field and open action button in the raw moves list, and the
inherited stock move form view adds explicit manufacturing origin fields in the
traceability section.
