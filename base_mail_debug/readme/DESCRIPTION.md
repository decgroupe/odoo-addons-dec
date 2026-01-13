This module adds detailed debug logs for the full e-mail flow in Odoo.

- Incoming e-mails are logged with key RFC headers so routing issues are easier to diagnose.
- New `mail.message` records are logged with sender, recipients, subject, and target record details.
- Outgoing e-mails are logged before SMTP send, including addressing headers and message id.
- HTML bodies of created messages are optionally written to the configured screenshots directory for inspection.

## Technical details

**Incoming e-mail tracing (`mail.thread`)**

`message_process` is extended in `mail.thread` and calls `_debug_incoming_message` before delegating to `super()`. The helper normalizes payloads (bytes/string/XML-RPC binary), parses the message with `email.policy.SMTP`, aggregates `Received` headers, and logs a structured summary.

**mail.message normalization and creation logs (`mail.message`)**

`create` is overridden with `@api.model_create_multi`. Before creation, `_ensure_create_values` removes falsey `email_from` and `reply_to` keys so upstream defaults can be applied. After creation, each message is logged with metadata (message type, author, recipients, layout, related model/record). When a body is present, it is dumped to a temporary `.html` file under `tools.config["screenshots"]`.

**Outgoing e-mail tracing (`ir.mail_server`)**

`send_email` is extended in `ir.mail_server` and calls `_debug_outgoing_message` before `super()`. The helper logs message headers such as `Message-Id`, sender/recipient fields, and subject to assist SMTP debugging.
