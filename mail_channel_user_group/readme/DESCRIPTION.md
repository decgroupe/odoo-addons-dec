When a message is posted from a `discuss.channel`, Odoo classifies every
recipient as a *customer* regardless of whether they are an internal user or an
external contact. This prevents email templates from applying user-specific
layouts or buttons that are only meaningful for internal users.

This module restores the standard recipient group classification so that:

- Internal users (Odoo users with a login) are placed in the **user** group.
- External contacts remain in the **customer** group.

The "See Channel" button is intentionally hidden in both cases because it is
not relevant in channel notification emails.

## Technical details

**`discuss.channel._notify_get_recipients_groups` override**

In Odoo 18.0, `discuss.channel` overrides `_notify_get_recipients_groups` and
replaces every non-customer group lambda with `lambda partner: False`, forcing
all recipients into the `customer` group.

This module extends `discuss.channel` and restores the `user` group lambda to
`lambda pdata: pdata["type"] == "user"` after calling `super()`. The
`has_button_access` flag is set to `False` for the `user` group to suppress the
"See Channel" action button in the notification email.
