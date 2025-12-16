This module adds a merge action on helpdesk tickets so users can consolidate
duplicate or overlapping tickets into a single destination ticket.

- It provides a list action to launch a merge wizard directly from tickets.
- It lets users choose which selected ticket remains as the destination.
- It redirects related documents to the kept ticket during the merge process.
- It removes source tickets after merge to keep the backlog clean.

## Technical details

**Wizard model**

The module defines `merge.helpdesk.ticket.wizard` as a transient model that
inherits `merge.object.wizard` from `base_merge` and targets
`helpdesk.ticket` records.

**Security and action visibility**

The window action is bound to the helpdesk ticket list view and restricted to
group `helpdesk_merge.res_group_do_merge`. The wizard also performs a runtime
group check in `_merge` and raises `AccessDenied` for unauthorized users.

**Merge execution behavior**

The `_merge` override delegates to the parent logic with
`mail_auto_subscribe_no_notify=True` in context to avoid auto-subscribe
notifications while merging records.

**Source record deletion**

The `_delete_source_objects` override calls the parent method on a sudoed
recordset, ensuring source ticket cleanup can complete without access-right
issues.
