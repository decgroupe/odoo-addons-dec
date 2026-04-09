# Migration Notes: 14.0 -> 18.0

## Overview

This document records the analysis, decisions, and changes made when migrating
`mail_channel_user_group` from 14.0 to 18.0.

---

## Key API Changes Discovered

### 1. `mail.channel` -> `discuss.channel`

In Odoo 18.0, the `mail.channel` model was renamed to `discuss.channel`. It is defined
in:

```
odoo/addons/mail/models/discuss/discuss_channel.py
```

The `_name = 'discuss.channel'` and it inherits from `mail.thread`,
`mail.alias.mixin.optional`, and `image.mixin`.

### 2. `_notify_get_groups` -> `_notify_get_recipients_groups`

The notification group classification API changed completely:

| 14.0                                                  | 18.0                                                                             |
| ----------------------------------------------------- | -------------------------------------------------------------------------------- |
| `_notify_get_groups(self, msg_vals=None)`             | `_notify_get_recipients_groups(self, message, model_description, msg_vals=None)` |
| `_notify_compute_recipients(self, message, msg_vals)` | `_notify_get_recipients(...)`                                                    |
| `_notify_classify_recipients(...)`                    | `_notify_get_recipients_classify(...)`                                           |

### 3. `channel_email` recipient type removed

In 14.0, `discuss.channel` (then `mail.channel`) introduced a custom `channel_email`
recipient type. Three method overrides in `mail.thread` relied on this type:

- `_notify_compute_recipients` - injected `channel_email` into recipients
- `_notify_get_groups` - defined groups for `channel_email`
- `_notify_classify_recipients` - routed `channel_email` recipients

In 18.0, this type **no longer exists**. All three overrides became obsolete.

### 4. How `discuss.channel` forces all recipients to `customer` in 18.0

The 18.0 `discuss.channel._notify_get_recipients_groups` forces all non-customer group
lambdas to `lambda partner: False`:

```python
# (from odoo/addons/mail/models/discuss/discuss_channel.py)
for index, (group_name, group_func, group_data) in enumerate(groups):
    if group_name != "customer":
        groups[index] = (group_name, lambda partner: False, group_data)
```

This is the behavior our module overrides.

---

## What the 14.0 Module Did

The 14.0 module had two models:

### `mail.channel` (in `mail_channel.py`)

Overrode `_notify_get_groups` to define groups for the `channel_email` recipient type.
Compared invited groups against `res.groups` records to decide if a recipient was an
internal user or customer.

### `mail.thread` (in `mail_thread.py`)

Three overrides:

1. `_notify_compute_recipients` - tagged channel recipients as `channel_email`
2. `_notify_get_groups` - defined `channel_email` group with user-group logic
3. `_notify_classify_recipients` - routed `channel_email` to correct group

---

## Migration Strategy

Since `channel_email` no longer exists, the entire 14.0 architecture collapsed into a
single override. The logic simplification:

**14.0**: inject custom type -> intercept in mail.thread -> check groups via ORM
**18.0**: override `_notify_get_recipients_groups` in `discuss.channel` directly,
restore `user` group lambda using `pdata['type'] == 'user'` (standard type available in
18.0 recipient data)

The `pdata['type']` field in 18.0 already contains `'user'` for internal users and
`'customer'` for external partners, so no ORM lookup needed.

---

## Files Changed

### Renamed / Rewritten

| Old path                 | New path                    | Reason                            |
| ------------------------ | --------------------------- | --------------------------------- |
| `models/mail_channel.py` | `models/discuss_channel.py` | model rename to `discuss.channel` |

### `models/discuss_channel.py` (new)

```python
class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        for index, (group_name, _group_func, group_data) in enumerate(groups):
            if group_name == "user":
                group_data["has_button_access"] = False
                groups[index] = (
                    group_name,
                    lambda pdata: pdata["type"] == "user",
                    group_data,
                )
        return groups
```

Key design decisions:

- Call `super()` first (which applies the `lambda partner: False` override)
- Then restore only the `user` group with the correct lambda
- Set `has_button_access = False` because the "See Channel" button is irrelevant for
  channel message emails

### `models/mail_thread.py` (emptied)

All three method overrides removed - they depended on `channel_email` type that no
longer exists. The class is kept as an empty `AbstractModel` for historical reference.

### `models/__init__.py`

```python
# before
from . import mail_channel
from . import mail_thread

# after
from . import discuss_channel
from . import mail_thread
```

---

## Tests

### `tests/common.py`

Base class `MailChannelUserGroupCommon` using `setUpClass` (not `setUp`) with:

- `cls.user_internal` = `base.user_demo` (internal user)
- `cls.partner_internal` = demo user's partner
- `cls.channel` = a `discuss.channel` created via `channel_create()`
- demo partner added as member via `add_members()`

### `tests/test_mail_channel_user_group.py`

Two tests:

**test_01** - `test_01_user_group_restored_for_internal_users`

- Posts a message on the channel
- Calls `_notify_get_recipients_groups` directly
- Asserts `user` group exists in the returned list
- Asserts the `user` group lambda returns `True` for a recipient with `type=='user'`
- Asserts `has_button_access` is `False`

**test_02** - `test_02_customer_recipient_not_classified_as_user`

- Same setup
- Asserts the `user` group lambda returns `False` for a recipient with
  `type=='customer'`

**Test results**: 2/2 passed, 0 failures, 0 errors (run against
`demo18_mail_channel_user_group` database)

---

## Commit History

```
[MIG] mail_channel_user_group: Migration to 18.0
[IMP] mail_channel_user_group: add tests and README
```
