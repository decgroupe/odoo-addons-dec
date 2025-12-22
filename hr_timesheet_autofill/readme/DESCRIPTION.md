This module helps users create timesheets faster by reusing values from a
previous timesheet line.

- Adds an Auto-fill selector on timesheet forms while creating a new line.
- Lets users search previous entries with enriched labels showing project,
  task, employee, and description.
- Copies key fields from the selected entry to reduce repetitive typing.

## Technical details

**Model extension**

The module extends `account.analytic.line` with
`autofill_from_analytic_line_id`. An onchange on this field copies values from
the selected source line based on `get_autofill_fields()` (default: `name`,
`project_id`, `task_id`).

**Create flow**

The `create()` override removes `autofill_from_analytic_line_id` from incoming
values before persistence, so the helper reference is never stored on final
timesheet entries.

**Search behavior**

`name_search()` is enhanced when `autofill_name_search` is present in context:
it builds an OR/AND domain across configured autofill fields for each token
with at least 3 characters, applies `autofill_search_order`, and formats
results with additional details for quick identification.

**Views**

The module adds the auto-fill field to both a rewritten primary timesheet form
and an inherited form extension, using context and domain options tailored to
the current user and autofill search mode.
