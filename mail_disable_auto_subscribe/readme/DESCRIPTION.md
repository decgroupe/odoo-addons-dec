This module lets each user and partner control whether they are automatically
added as a follower on Odoo records. Three independent opt-out flags are
available:

- **On message (@-mention)**: prevent being subscribed when a message is posted
  and you are the author or are @-mentioned.
- **On tag**: prevent being subscribed when a tag assigned to a record would
  normally trigger follower subscription via autofollow.
- **On activity**: prevent being subscribed when an activity is created or
  reassigned to you.

The flags are exposed in the user preferences form and in the partner form, so
they can be managed by the user themselves or by an administrator.

## Technical details

**Per-partner auto-subscribe flags**

Three Boolean fields (`auto_subscribe_on_message`, `auto_subscribe_on_tag`,
`auto_subscribe_on_activity`) are added to `res.partner` (all default to
`True`). The same fields are surfaced on `res.users` via the partner relation.

**Message-post subscription (`mail.thread`)**

`message_post` is overridden: when the effective author's
`auto_subscribe_on_message` flag is `False`, `mail_create_nosubscribe=True` is
injected into the context before calling `super()`, which prevents the base
Odoo logic from subscribing them.

**Tag autofollow subscription (`mail.thread`)**

`_message_subscribe` is overridden: when the call originates from an autofollow
context (`mail_post_autofollow`), partners whose `auto_subscribe_on_tag` is
`False` are filtered out before delegating to `super()`.

**Activity-triggered subscription (`mail.activity`)**

`mail.activity.create` and `write` are overridden: the default Odoo
auto-subscription is suppressed via `mail_activity_noautofollow=True`, and
subscription is then performed manually only for users whose
`auto_subscribe_on_activity` flag is `True`.

**Subtype exclusion per model (`mail.message.subtype`)**

A `excluded_res_model_ids` Many2many field is added to `mail.message.subtype`.
`_default_subtypes` is overridden to exclude subtypes whose
`excluded_res_model_ids` contains the current model, unless the subscription
originates from a manual call (`manual_message_subscribe` context key).

**User self-write permission (`res.users`)**

The `SELF_WRITEABLE_FIELDS` property is extended to include the three
auto-subscribe fields, allowing users to update their own preferences without
needing administrator access.
