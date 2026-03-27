This module improves incoming email routing when standard thread references
cannot be resolved.

- It uses data from the mail tracking pixel embedded in the email body as a
  fallback source.
- It helps replies continue in the correct chatter thread when message headers
  are incomplete or unusable.

## Technical details

**Fallback routing in `mail.thread`**

The module inherits `mail.thread` and extends
`_message_route_get_thread_references`. It first keeps Odoo's default
resolution, then applies fallback logic only when no thread reference is found.

**Tracking pixel parsing and validation**

The fallback extracts `<db>/<tracking_email_id>/<token>` from the
`/mail/tracking/open/.../blank.gif` URL found in the email body. It validates
that the extracted database matches the current database before continuing.

**Message-id recovery**

After validation, it searches `mail.tracking.email` by ID and token, then
returns `mail_message_id.message_id` so Odoo can route the email to the
correct existing thread.
