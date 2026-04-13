This module replaces the default mailing-list notification system with
QWeb-based email rendering, the same engine used by other transactional
emails in Odoo.

- Notification emails sent to group members are rendered with the
  `mail_qweb` layout, giving them a consistent look and feel with other
  Odoo emails.
- The "also notified" section of each email lists recipients grouped by
  type (internal users, portal users, external partners) with their
  avatar and notification mode.
- A custom footer replaces the default plain-text footer, showing the
  group name, mailing address, and an unsubscribe link.

## Technical details

**QWeb rendering pipeline**

`MailGroup._notify_members` is overridden to build the email body using
`ir.qweb._render("mail.mail_notification_light", ...)` instead of the
default Odoo approach. The rendering context is prepared by
`_notify_by_email_prepare_rendering_context`, which adds
`content_message_align` (computed by `mail_qweb`) and
`notification_group_name` so the template can conditionally show the
"also notified" block.

**Recipient classification**

`MailGroup._notify_get_recipients` delegates to
`MailGroupMember._get_recipient_data`, which mimics
`mail.followers._get_recipient_data` but for group members. Each member
is classified as `user` (internal), `portal` (portal user), or
`customer` (email-only / no Odoo account).
`MailGroup._notify_get_recipients_classify` reuses
`mail.thread._notify_get_recipients_groups` to assign each member to the
correct notification group and attaches the `_members` recordset and
`_members_notif_mode` mapping to every group so the QWeb template can
iterate over them.

**Footer template**

`mail_group_qweb.mail_group_footer` fully replaces Odoo's default
`mail_group.mail_group_footer` template. It is rendered per-member by
`MailGroup._get_footer` and appended to the HTML body before the
`mail.mail` record is created.

