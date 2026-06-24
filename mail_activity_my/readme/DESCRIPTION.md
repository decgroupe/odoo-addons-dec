This module provides an abstract mixin (`mail.activity.my.mixin`) that extends
any model with user-specific activity fields. Unlike the standard activity fields
that aggregate all users' activities, these fields only reflect the activities
assigned to the currently logged-in user.

The following computed fields are added to models inheriting the mixin:

- **My Activities** (`activity_my_ids`): activities assigned to the current user
- **My Activity State** (`activity_my_state`): overdue / today / planned, based
  on the current user's next activity
- **My Next Activity Type** (`activity_my_type_id`): type of the next activity
- **My Deadline** (`activity_my_date_deadline`): deadline of the next activity
- **My Next Activity Summary** (`activity_my_summary`): summary text
- **My Activity Type Icon** (`activity_my_type_icon`): icon of the activity type

An `action_snooze_my` method is also provided to postpone the next activity by
7 days (or reschedule it to today + 7 days if it is already overdue).

Kanban and list view widgets are provided as OWL components (`kanban_activity_my`
and `list_activity_my`) that display user-specific activity indicators.

## Technical details

- Mixin model: `mail.activity.my.mixin`
- JS components: `KanbanActivityMy`, `ListActivityMy`, `ActivityButtonMy`
- Overrides `_read_group_groupby` for grouping by `activity_my_state` with
  user filtering at the SQL level
