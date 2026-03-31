This module improves the reliability of mail messages in two ways:

- Messages are always linked to the correct document name, even when the name
  was accidentally cleared before saving.
- When a message is sent by someone whose email address has no display name,
  their address is shown as-is instead of being replaced by the generic
  notification sender, making it easier to identify who wrote the message.

## Technical details

**Auto-naming of mail messages**

Odoo's default `mail.message` create logic only sets `record_name` when the
field is absent from the values dict. If a caller explicitly passes
`record_name=False`, the name is left empty. This module overrides `create` to
also fill `record_name` in that case, as long as `model` and `res_id` are
provided and `default_record_name` is not set in the context.

**Email display-name reformatting**

When a message is authored by a plain e-mail address with no display name
(e.g. `yanapa@laposte.net`), Odoo would show the notification sender address
instead of the original author address. This module overrides
`_message_compute_author` on `mail.thread` to reformat such bare addresses into
the `"address <address>"` form (e.g.
`yanapa@laposte.net <yanapa@laposte.net>`), so the author's address is always
visible to recipients regardless of the outgoing mail server configuration.
