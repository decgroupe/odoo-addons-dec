This module sends reminder emails to users listing their upcoming and overdue
activities. Each email contains action buttons so the user can act on any
activity directly from their inbox, without logging in to Odoo.

- **Close**: marks the activity as done.
- **Cancel**: deletes the activity.
- **Snooze**: postpones the deadline by a chosen amount of time (days, weeks,
  months, or years).

Each user's reminder is protected by a personal, revocable access token so that
only the intended recipient can act on their own activities.

## Technical details

**Email reminder (`res.users`)**

`send_activity_reminder` searches the user's open activities (grouped by
activity type via `_get_group_activity_ids`) and renders
`email_template_activity_reminder`. If the user has no open activities the
method is a no-op. A new UUID token is generated on demand by
`generate_new_activity_reminder_access_token` and stored in
`activity_reminder_access_token`.

**Snooze (`mail.activity`)**

`action_snooze_custom(unit, value, from_date=None)` extends the deadline of each
activity in the recordset. The new deadline is computed from the current
deadline (or `from_date` if provided, but never in the past). Supported units
are `day`, `week`, `month`, and `year`. A localised notification is appended
to the activity note so the change is traceable.

**HTTP controller (`MailActivityReminderController`)**

Three public `GET` routes under `/api/reminder/v1/activity/<id>/` handle
`close`, `cancel`, and `snooze/<value>/<unit>`. Each route validates the
`token` query parameter against `activity_reminder_access_token` via
`_get_user_id`. On success the action is performed and a QWeb confirmation
page is rendered; on failure an invalid-token or not-found page is rendered
instead. The controller inherits from `HttpControllerUser` (provided by
`base_controller_user`) to carry the user's language and timezone into the
request context.
