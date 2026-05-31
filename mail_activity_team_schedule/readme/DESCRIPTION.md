This module improves activity planning when a team is assigned.

- If an activity has no assigned user but has an activity team, the displayed
	assigned resource is the team name.
- If a user is assigned, the standard user name display is kept.

## Technical details

**Assigned resource fallback**

The module extends `mail.activity` and overrides
`_compute_assigned_resource`. It first calls `super()` to preserve native
behavior, then applies a fallback for records with `team_id` when
`assigned_resource` is still empty.

**Compatibility with scheduling modules**

The behavior is intentionally minimal and relies on fields introduced by
`mail_activity_team` and `mail_activity_schedule`, without changing write/create
flows or view definitions.
