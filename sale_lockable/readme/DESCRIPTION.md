This module lets sales teams lock a quotation in draft so only the assigned
salesperson (or an administrator) can manage sensitive changes.

- Add a "Lock Changes" action on draft quotations to freeze key fields.
- Show a visible warning banner when a quotation is locked.
- Allow only the quotation owner or an administrator to lock or unlock it.
- Automatically unlock the quotation when it is confirmed.

## Technical details

**Draft lock workflow**

The module extends `sale.order` with `locked_draft` and a computed `same_user`
flag. It adds `action_draft_lock` and `action_draft_unlock`, and enforces
permission checks in `_check_lock_unlock` so only the assigned salesperson or
an admin can toggle the lock. It also posts a chatter message when the lock
state changes.

**Write protection on configured fields**

The `write` override calls `_update_lock_state`, which reads
`sale_lockable.fields` from `ir.config_parameter` and blocks edits on those
fields when the quotation is locked by another user. If a protected write is
attempted, `_check_lock_changes` raises a `UserError` listing the translated
field labels.

**UI integration**

The inherited sale order form view adds lock/unlock buttons, an alert banner
for locked draft quotations, and hidden helper fields used by view logic.
