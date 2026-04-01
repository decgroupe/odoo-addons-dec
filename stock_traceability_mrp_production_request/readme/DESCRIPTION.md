Extends stock traceability with production request awareness.

When a stock move is linked to a manufacturing request (`mrp.production.request`),
the traceability status and navigation button reflect the request instead of the
default upstream information:

- The move status displays the request name and its current state (with emoji).
- The "view created item" button opens the request form, or jumps directly to
  the linked manufacturing orders when they exist.
- The button is visible as soon as a production request is linked, even before
  any manufacturing order has been created.

## Technical details

**Production request status symbol**

`mrp.production.request` is extended with a `state_symbol` computed field and a
`get_head_desc()` method that returns a `(head, desc)` pair used by the
traceability status widgets.

**Stock move overrides**

`stock.move._get_mto_status()` is overridden: when `created_mrp_production_request_id`
is set, the method returns the request head/desc formatted string instead of
delegating to the parent.

`stock.move.action_view_created_item()` is overridden: it redirects to
`action_view_mrp_productions()` when manufacturing orders exist on the request, or
to `action_view()` (request form) otherwise.

`stock.move._get_mto_created_items()` is overridden to include the linked
production request, which drives the `action_view_created_item_visible` boolean
field used to show or hide the navigation button.

`stock.move._compute_action_view_created_item_visible()` is overridden with an
additional `@api.depends("created_mrp_production_request_id")` so the visibility
field is properly recomputed whenever the production request link changes.
