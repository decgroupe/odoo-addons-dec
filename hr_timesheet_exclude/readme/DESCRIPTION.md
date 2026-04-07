This module allows you to exclude specific projects or tasks from timesheet
accounting analysis.

- **Project exclusion**: mark a project as excluded so that all timesheet
  entries logged on it are hidden from the analysis view.
- **Task exclusion**: mark an individual task as excluded so that its
  timesheet entries are removed from the analysis view, regardless of the
  project setting.
- **Computed indicator**: each timesheet line receives a `posted_in_timesheet`
  boolean that is automatically recomputed whenever the exclusion flag on the
  related project or task changes, and a search filter lets users limit the
  analysis view to lines that are effectively posted.

## Technical details

**`posted_in_timesheet` computed field**

A stored `Boolean` field `posted_in_timesheet` is added to
`account.analytic.line`. It is computed by
`_compute_posted_in_timesheet`, which depends on
`project_id.exclude_from_timesheet` and `task_id.exclude_from_timesheet`.
The field is `True` by default and set to `False` as soon as the related
project or task is flagged as excluded.

**`exclude_from_timesheet` flag**

A `Boolean` field `exclude_from_timesheet` is added to both
`project.project` and `project.task`. Both fields are hidden behind
`base.group_no_one` in the UI so that only technical users can set them.

**Search view**

A filter *Posted in Timesheets* (`domain="[('posted_in_timesheet', '=', True)]"`)
is injected into the timesheet analysis search view via an inherited view on
`account.analytic.line`.

**Form view — analytic line**

The `exclude_from_sale_order` field (from `sale_timesheet_line_exclude`) is
added to the timesheet form view, and the `amount` field is hidden when a
line is excluded from the sale order.
