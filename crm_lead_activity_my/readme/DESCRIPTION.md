This module enhances CRM opportunity views by displaying activities that belong
to the current user, rather than all activities assigned to any user.

- **List view**: adds a dedicated "My Activities" column with a custom widget,
  alongside a snooze button that postpones the next personal activity by 7 days.
- **Kanban view**: replaces the default activity progressbar with one filtered
  on the current user's activities, and adds a snooze shortcut on each card.

## Technical details

**Mixin inheritance**

`crm.lead` inherits `mail.activity.my.mixin`, which provides the computed
fields `activity_my_ids`, `activity_my_state`, `activity_my_date_deadline`,
and the `action_snooze()` method.

**View extensions**

The list view (`crm.crm_case_tree_view_oppor`) is extended to insert the
`list_activity_my` widget before the native `my_activity_date_deadline` field
and to add an `activity_my_state` hidden field used to control the snooze
button visibility.

The kanban view (`crm.crm_case_kanban_view_leads`) is extended to declare the
user-scoped activity data fields, replace the progressbar with one based on
`activity_my_state`, inject a deadline badge before the footer, and add the
`kanban_activity_my` widget with a snooze link.
