This module allows you to automatically redirect Odoo activities to a specific
user based on configurable rules. Instead of activities being assigned to the
default user (e.g. the category manager), you can route them to whoever is
actually responsible in your organization.

- **Rule-based redirection**: define rules that intercept activities and
  reassign them to a target user based on model, activity type, initial
  assignee, QWeb template, or a regex pattern on the activity note.
- **Flexible matching**: combine multiple criteria in a single rule - all
  conditions must match for the redirect to apply (first matching rule wins).
- **Activity history**: each rule keeps a rolling history of the last 5
  intercepted activities for audit purposes.
- **Settings integration**: manage redirection rules directly from the
  General Settings page under the Emails section.

## Technical details

**Redirection model**

A new model `mail.activity.redirection` stores the rules. Each rule defines a
target `user_id` and optional filters: `initial_user_ids` (original assignees),
`model_ids` (Odoo models), `activity_type_ids`, `qweb_templates` (QWeb views
used to render the note), and `regex_pattern` (applied to the activity note).
Rules are evaluated in sequence order; the first match stops the evaluation.

**Activity interception**

`mail.activity.mixin.activity_schedule` is overridden in
`models/mail_activity_mixin.py`. Before creating the activity, all active
rules are matched against the scheduling parameters. If a rule matches, the
`user_id` in `act_values` is replaced with the rule's target user. After
creation, `mail.activity._link_to_mail_activity_redirection` links the new
activity to the rule's history (capped at 5 entries).

`_activity_schedule_with_view` is also overridden to forward the original
QWeb template XML ID to `activity_schedule` via `act_values`, allowing
template-based matching to work correctly.
