This module links HR timesheets to manufacturing orders, enabling time
tracking directly on production orders.

- Employees can log timesheet entries (analytic lines) against a specific
  production order.
- Each production order displays planned hours, total hours spent, progress
  percentage, and remaining hours.
- When the first timesheet entry is saved on a confirmed production order, the
  order is automatically moved to the "In Progress" stage.
- Timesheets are only enabled on a production order when it is attached to a
  project (`allow_timesheets` flag). Orders created without a project skip
  automatic project creation.
- When the project linked to a production order changes, all related timesheet
  lines are updated to reflect the new project.

## Technical details

**`mrp.production` extension**

Adds the following fields: `allow_timesheets` (Boolean, default False),
`planned_hours` (Float, tracked), `timesheet_ids` (One2many to
`account.analytic.line`), `total_hours` (computed from timesheet unit amounts),
`progress` (computed as `total_hours / planned_hours * 100`), and
`remaining_hours` (computed as `planned_hours - total_hours`).

The `create` override separates records with and without `allow_timesheets` so
that orders without timesheets are created with the `mrp_project_auto_disable`
context, preventing automatic project creation from `mrp_project_auto`.

`_constrains_project_timesheets` propagates a project change to all linked
timesheet lines. `_compute_total_hours` calls `action_start()` automatically
when a first timesheet entry is recorded on a confirmed order.

**`account.analytic.line` extension**

Adds `production_id` (Many2one to `mrp.production`, restricted to
`mrp.group_mrp_user`), related fields `production_partner_id`,
`production_partner_name`, `production_product_id`,
`production_product_name` (all stored), and a computed
`production_identification` that formats the production order identifiers.

A dynamic binary domain field `production_id_domain` filters available
production orders by the currently selected project. The `onchange_production_id`
handler pre-fills the project from the production order when none is set yet.
