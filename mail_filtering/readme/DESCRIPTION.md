This module controls where outgoing emails can be sent from, per SMTP server.

- Add an "Allowed Databases" setting on each outgoing mail server.
- Allow all databases with `*`, or restrict sending to a comma-separated list.
- Block email sending when the current database is not allowed for the selected
  server.
- Use the global `db_process_email_allowedlist` server configuration parameter
  as a fallback allowlist when a server rule does not allow the current
  database.

## Technical details

**Mail server selection tracking**

The module extends `ir.mail_server.connect` and stores the selected server id
on the SMTP session (`mail_server_id`). This ensures the mail sending layer can
reliably identify which server was used.

**Queue processing behavior**

The module extends `mail.mail.process_email_queue` to set the context key
`raise_if_send_not_allowed=True` so blocked sends are explicit during queue
processing.

**Outgoing mail filtering**

The module extends `mail.mail._send` and evaluates permission in this order:

1. `ir.mail_server.allowed_databases` on the effective outgoing server.
2. Global allowlist from `db_process_email_allowedlist` (cached by
   `_get_db_process_email_allowedlist`).

If the current database is not allowed, the method logs the block and returns
`False` (or raises an exception when the context requires it).
