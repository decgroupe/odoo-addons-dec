When a time off request is validated, this module generates one timesheet
line per work interval instead of one line per day. Each generated line
carries the precise start time of the interval in the **Start Time**
(`date_time`) field, making the timesheets compatible with the time-control
workflow provided by *HR Timesheet Time Control*.

- **Per-interval timesheets**: a full-day leave on a calendar with a morning
  and afternoon block produces two timesheet lines (one at 08:00, one at
  13:00), each reflecting the exact duration of that block.
- **Accurate start times**: the `date_time` field on each line is set to the
  UTC start of the corresponding work interval, so time-tracking widgets
  display the correct clock-in time.
- **Consistent with leave type settings**: the project and task come from
  the leave type when a company is set, or from the company's internal
  project and "Time Off" task otherwise — identical to the standard
  `project_timesheet_holidays` logic.

## Technical details

**Override of `_generate_timesheets`**

`hr.leave._generate_timesheets` is overridden. Leaves whose leave type has
`timesheet_generate = False` are delegated to the standard implementation
via `super()`. For the remaining leaves the override:

1. resolves the project and task from the leave type (company-specific) or
   from the company defaults;
2. calls `resource.calendar._work_intervals_batch()` with
   `compute_leaves=False` to obtain the exact work intervals for the
   employee's calendar in the leave date range;
3. for each interval, builds analytic-line vals including `date_time` (UTC
   start of the interval) and `unit_amount` (interval duration in hours);
4. unlinks any previously generated timesheets for the same leaves before
   creating the new ones (safe to call for regeneration).

The `_prepare_timesheet` helper assembles the vals dict for a single
interval and is kept separate to make it easy to override in downstream
modules.

