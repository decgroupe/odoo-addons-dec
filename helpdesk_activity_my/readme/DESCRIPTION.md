This module adds user-focused activity indicators to Helpdesk tickets.

- List view shows the current user's activities and their nearest deadline.
- Kanban cards highlight the current user's activity state with a progress bar.
- A Snooze 7d action lets the user postpone their own next activity directly
	from list and kanban views.

## Technical details

**Model extension**

The module extends `helpdesk.ticket` with `mail.activity.my.mixin` in
`models/helpdesk_ticket.py`. This brings the computed fields
`activity_my_ids`, `activity_my_state`, and `activity_my_date_deadline` to
ticket records.

**List view customization**

The inherited list view adds `activity_my_ids` and
`activity_my_date_deadline` after `user_id`, keeps `last_stage_update` with
the `remaining_days` widget, and adds the `action_snooze` button.

**Kanban view customization**

The inherited kanban view replaces the default progressbar to use
`activity_my_state`, then injects `activity_my_state` and `activity_my_ids`
next to `activity_ids` and exposes a kanban `action_snooze` object action.
