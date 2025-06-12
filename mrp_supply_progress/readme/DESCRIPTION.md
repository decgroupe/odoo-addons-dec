This module tracks how much a manufacturing order is supplied before production starts.

- It adds a Supply Progress percentage on manufacturing orders.
- It marks each raw material move as received when quantities are available or upstream moves are done.
- It introduces workflow visibility with dedicated stages for supplying and ready-to-build states.
- It displays supply progress in list, form, and staged kanban views.
- It provides a scheduled action and a manual server action to recompute supply progress.

## Technical details

**Supply progress computation**

The module extends mrp.production with supply_progress and computes it in
_compute_supply_progress from non-cancelled move_raw_ids that have received=True.
It also adds run_supply_progress_update_scheduler to recompute recent active
productions and action_update_supply_progress for manual recomputation.

**Raw move availability flag**

The module extends stock.move with a stored received field computed in
_compute_received. A move is received when it is done, when make_to_order
dependencies are done or cancelled, or when make_to_stock quantities are
sufficiently reserved.

**Stage and UI integration**

The module extends stage resolution methods on mrp.production to use
supplying and build_ready stages based on supply status. It adds both stage
records in data/mrp_production_stage.xml and a periodic cron in
data/mrp_production_cron.xml. It also extends production list, form, and
staged kanban views to render progress indicators and the received flag.
