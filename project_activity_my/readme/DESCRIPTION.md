This module adds "My Activities" columns to project and task views, allowing each user to see their personal pending activities directly on the project kanban and task list views.

- Each user only sees activities assigned to them, not all activities on the record.
- A progress bar shows the state of personal activities (overdue / today / planned).
- Kanban cards and list rows display a compact list of personal next activities with the same look and feel as the standard activity widget.

## Technical details

**Models**

- `project.project` inherits `mail.activity.my.mixin` to get the `activity_my_ids`, `activity_my_state`, and related computed fields.
- `project.task` inherits `mail.activity.my.mixin` the same way.

**Views**

- Project kanban view (`view_project_kanban`): adds the progressbar for `activity_my_state` and the `kanban_activity_my` widget showing the current user's next activities.
- Task list view (`view_task_tree2`): adds the `list_activity_my` widget next to the standard activity column so each user sees only their own pending activities.
