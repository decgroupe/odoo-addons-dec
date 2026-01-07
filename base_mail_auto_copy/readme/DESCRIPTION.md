This module extends outgoing email routing on mail servers.

- It can automatically add the sender as a hidden recipient so users keep a
	copy of emails they send from Odoo.
- It can add fixed Cc and Bcc recipients on every outgoing email sent through
	the selected mail server.
- It can skip the automatic sender copy for ignored addresses, for users who
	disabled that preference, and for messages sent from internal chats or mail
	groups.

## Technical details

**Mail server behavior**

The module extends `ir.mail_server` and adds the configuration fields
`auto_add_sender`, `ignored_aas_addresses`, `auto_cc_addresses`, and
`auto_bcc_addresses`.

**Header injection**

Before delegating to the standard `send_email()` implementation, the override
resolves the active mail server with `get_mail_server()`, then updates the
message headers through `_update_cc_addresses()` and
`_update_bcc_addresses()`.

**Sender copy safeguards**

`_update_bcc_addresses()` looks up the related `mail.message` from the RFC2822
message identifier. It suppresses sender auto-BCC when the source message comes
from `mail.channel` or `mail.group`, when the sender address is listed in the
ignored addresses, when no matching internal user is found, or when the user's
`copy_sent_email` preference is disabled.
