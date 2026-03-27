This module lets you temporarily disable mail notifications when posting messages from business flows that should stay silent.

- Disable both notification channels at once by setting `mail_partner_notify_disable` in context.
- Disable only outgoing e-mail notifications by setting `mail_partner_notify_disable_email`.
- Disable only inbox/chat notifications by setting `mail_partner_notify_disable_chat`.

## Technical details

**Global notification bypass**

The module inherits `mail.thread` and overrides `_notify_thread_by_email` and
`_notify_thread_by_inbox`. When `mail_partner_notify_disable` is present in
`env.context`, both methods return early and no notification records are
created for that message.

**E-mail-only bypass**

In `_notify_thread_by_email`, when
`env.context['mail_partner_notify_disable_email']` is set, the method exits
before calling `super()`, which prevents `mail.mail` creation and therefore
stops outgoing e-mail delivery for that post.

**Inbox-only bypass**

In `_notify_thread_by_inbox`, when
`env.context['mail_partner_notify_disable_chat']` is set, the method exits
before the standard inbox notification flow, so `mail.notification` entries for
the inbox channel are not generated.
