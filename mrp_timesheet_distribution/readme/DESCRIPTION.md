This module adds a wizard that allows distributing a block of working time
evenly across multiple manufacturing orders (MOs) in a single operation.

- **Time distribution**: select one or more MOs, enter a total duration and a
  start date/time; the wizard splits the time into equal contiguous intervals,
  one per MO, and creates the corresponding timesheet entries automatically.
- **Break exclusion**: optionally define a break window (start/end) to skip;
  the wizard splits the work period around the break and re-distributes the
  remaining time accordingly.
- **Reason tracking**: pick a predefined reason (e.g. *Layout & Wiring*) or
  choose *Other* and type a free-text label that becomes the timesheet entry
  name.
- **Continue mode**: an *Distribute & Continue* button reopens the wizard with
  the start time set to the end of the last distributed interval, making it
  easy to log a full working day step by step.

## Technical details

**Wizard model** (`mrp.distribute.timesheet`)

The wizard computes a `Many2many` preview field `timesheet_line_ids` (model
`mrp.distribute.timesheet.line`) using a `@api.depends` compute method.  Each
line holds `start_time`, `end_time`, the linked `project_id` and
`production_id`.  On confirmation, `_do_distribute` iterates over the preview
lines, resolves or creates the target `project.task` via `_get_or_create_task`,
and writes one `account.analytic.line` per interval.

**Break exclusion logic** is implemented entirely in
`_compute_timesheet_line_ids`: it detects whether the break window overlaps the
work period and, when it does, calls `_generate_timesheet_interval` twice — once
for the segment before the break and once for the segment after.

**Onchange helper** `onchange_date_time` reads the current user's resource
calendar to pre-fill `excluded_start_time` / `excluded_end_time` with the lunch
break times for the selected day.
