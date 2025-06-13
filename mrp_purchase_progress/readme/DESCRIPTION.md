This module adds purchase progress tracking on Manufacturing Orders so planners can quickly see how much of the required supply has already been purchased.

- It computes a purchase completion percentage based on make-to-order raw material moves linked to purchase flows.
- It shows this percentage in the Manufacturing Order form as a progress bar.
- It adds a dedicated purchase progress indicator in staged kanban cards when it is relevant to the current stage.
- It provides a server action and a scheduler entry point to refresh purchase progress values.

## Technical details

**Progress computation**

The module extends `mrp.production` with a stored computed float field
`purchase_progress`. The `_compute_purchase_progress` method filters raw
material moves to keep non-cancelled make-to-order moves that are connected to
purchase lines (directly or through origin moves). It then computes the ratio
between destination moves whose purchasing side is assigned/done and the total
eligible moves.

**Supply stage interaction**

`_is_supply_active` is extended so supply is still considered active when
purchase progress has started. The module also declares dependencies for stage
recomputation and computes `kanban_show_purchase_progress` to display the
kanban indicator only in supply-related contexts.

**UI and actions**

An inherited manufacturing form view adds `purchase_progress` in the
miscellaneous progress block with a progressbar widget. An inherited staged
kanban view injects `purchase_progress` and `kanban_show_purchase_progress`, and
renders a shopping-cart themed progress bar. A server action calls
`action_update_purchase_progress`, and `run_purchase_progress_update_scheduler`
updates recent non-cancelled productions with incomplete progress.
