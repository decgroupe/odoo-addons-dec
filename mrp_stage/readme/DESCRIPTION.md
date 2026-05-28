This module adds a computed stage field to manufacturing orders, allowing them
to be grouped and visualized in a Kanban view by production stage.

- Stages are automatically derived from the manufacturing order state (draft,
  confirmed, in progress, done, cancelled) and enriched by activity types and
  outgoing stock move states.
- Each stage can carry an icon (symbol), a sequence, a to-do flag, and a
  folded-in-kanban option.
- A dedicated Kanban color field lets users visually differentiate orders.
- Activity types can be linked to a production stage: when an activity of that
  type is open on an order, the order advances to the corresponding stage.
- When all finished-goods moves have been transferred, the order automatically
  moves to a "dispatch ready" stage.

## Technical details

**`mrp.production` extension**

The `stage_id` field is a stored, computed `Many2one` to `mrp.production.stage`.
`_compute_stage_id` calls `_get_stages_ref()` to resolve the well-known stage
XML IDs (`mrp_stage.stage_draft`, `mrp_stage.stage_confirmed`, etc.) and then
`_get_stage_from_state()` per record to pick the right stage. Activity-based
overrides are resolved by `_get_stage_from_activity()`, which selects the
activity type with the highest sequence that has a linked production stage.
The `stage_todo` field is a stored related field on `stage_id.todo` used as a
quick filter.

**`mrp.production.stage` model**

A new model holding stage definitions: name, code (unique), symbol, sequence,
fold, todo, and an optional default activity type. `_compute_display_name`
prepends the symbol to the name when present.

**`mail.activity.type` extension**

Adds a `production_stage_id` computed field (first element of
`production_stage_ids`) so that an activity type can trigger a stage transition
on the manufacturing order.

**`mail.activity` extension**

`action_done` and `action_close_dialog` return a multi-action response
(`ir.actions.act_multi`) that closes the dialog and performs a soft reload,
ensuring the Kanban stage is refreshed immediately.

**Post-install hook**

`post_init_hook` recomputes `stage_id` on all existing manufacturing orders
after the module is installed, so historical records are correctly staged.
