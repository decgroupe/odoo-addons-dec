This module keeps user logins aligned with their contact email and improves
how partner archiving impacts linked users.

- When a contact email changes, linked user logins are updated automatically
  when the login still matches the previous email.
- Contact managers can archive or unarchive a partner and propagate the same
  action to related portal users.
- Internal users are protected: only administrators can archive or unarchive
  them through partner actions.

## Technical details

**Partner write synchronization**

The module extends `res.partner.write` to keep a mapping of previous emails and
after write, synchronizes `res.users.login` for linked users when the previous
login matched the old contact email. Synchronization requires either the
`res_users_login_sync.group_user_login_sync` group or ownership of the user
being updated.

**Archive and unarchive propagation**

The module extends partner archive flows (`_archive_users` and
`_unarchive_users`) to propagate active state changes to related users, with
context flags to avoid recursion with `res.users.toggle_active` and user
creation side effects.

**Security and notifications**

Before partner-driven archive changes, `_check_archive_change` blocks
non-admin users from archiving internal users. Audit notes are posted with
`message_post_with_source`, and login updates notify users through
`res_users_login_sync.email_template_login_edit`.
