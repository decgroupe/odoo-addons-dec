This module allows setting a custom calendar meeting name per leave type, so
that calendar events created when a time-off request is approved carry a more
meaningful name instead of the default Odoo-generated one.

- **Custom meeting name**: each leave type can define a `Meeting Name` field.
  When set, this name is used as the prefix of the calendar event title
  instead of the leave type's display name.
- **Employee and duration**: the meeting title always includes the employee's
  name and the leave duration (in days or hours depending on the leave type
  configuration).

## Technical details

**`hr.leave.type`**

A new `Char` field `calendar_name` is added. It is exposed in the leave type
form view inside the *Configuration* group.

**`hr.leave`**

`_prepare_holidays_meeting_values` is overridden to rewrite the `name` key of
every meeting value dict returned by `super()`. The new name follows the
pattern `<calendar_name or display_name> : <employee_name>, <duration>`.
The duration is formatted as `%.2f hour(s)` for hour-based leave types and
`%.2f day(s)` for day-based ones.
