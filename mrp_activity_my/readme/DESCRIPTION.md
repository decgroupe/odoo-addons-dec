This module adds "My Activities" indicators to Manufacturing orders so each user can focus on their own next actions.

- List view: shows the current user's activity widget and keeps the order deadline easy to scan.
- Kanban view: shows the current user's activity widget and a progress indicator for next activities.

## Technical details

**Model extension**

The module extends `mrp.production` with `mail.activity.my.mixin`. That mixin provides user-scoped activity fields such as `activity_my_ids`, `activity_my_state`, and `activity_my_date_deadline`.

**View inheritance**

The module inherits the manufacturing order list and kanban views to inject the user-scoped activity fields. The list view adds `activity_my_ids` with the `list_activity_my` widget, while the kanban views add `activity_my_ids`, `activity_my_state`, a `progressbar`, and the `kanban_activity_my` widget.
