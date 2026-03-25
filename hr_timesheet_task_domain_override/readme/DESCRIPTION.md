This module allows selecting closed tasks on timesheet lines.

- Keeps the task selector restricted to tasks in the selected project.
- Preserves the base company and timesheet-enabled project filters.
- Optionally restores the default behavior (exclude closed tasks) through a context flag.

## Technical details

**Timesheet task domain override**

The module inherits `account.analytic.line` and overrides the `task_id` field
domain with a computed Binary domain field (`task_id_domain`). The domain is
computed in `_compute_task_id_domain`.

For every timesheet line, it always keeps the base filters on company and on
`project_id.allow_timesheets`.

When `project_id` is set:

- If context key `keep_hr_timesheet_task_domain` is true, it keeps the OCA
	default logic from `hr_timesheet_task_domain` and excludes closed states.
- Otherwise, it filters only by project and allows tasks in closed states.
