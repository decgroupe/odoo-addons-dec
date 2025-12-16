This module improves project task follow-up by creating and managing reminder
activities for assignment and planning.

- Adds dedicated activity types on tasks: **To Assign** and **To Plan**.
- Supports automatic reminder creation when a task is created in automatic mode
  and is missing an assignee or deadline.
- Automatically closes related reminders when the task is assigned, planned, or
  moved to a closed state.

## Technical details

**Project task extension**

The module inherits `project.task` and overrides `create` and `write`.

- In `create`, when context key `auto_activity` is enabled, it schedules:
  `project_activity.mail_activity_to_assign` when `user_ids` is empty, and
  `project_activity.mail_activity_to_plan` when `date_deadline` is empty.
- In `write`, it removes or marks activities as done according to updates:
  when `state` enters `CLOSED_STATES`, both activity types are unlinked; when
  `user_ids` is updated, the `to_assign` activity is completed; when
  `date_deadline` is updated, the `to_plan` activity is completed.

**Activity type data**

Two `mail.activity.type` records are defined for `project.task` in
`data/mail_activity_type.xml`:

- `mail_activity_to_assign` with icon `fa-user-plus` and delay `2` days,
- `mail_activity_to_plan` with icon `fa-calendar-plus-o` and delay `14` days.
