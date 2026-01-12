This module enriches assignment notification emails with additional context about
the assigned record.

- It adds an extra information block in assignment emails for users and
	activities.
- It displays field labels and formatted values so recipients can understand key
	details without opening the record first.

## Technical details

**QWeb rendering extension**

The module extends `ir.qweb` rendering to detect the assigned record from the
rendering values/context and injects an `extra_values` payload when the record
implements `_get_assigned_extra_values`.

**Extra field extraction and formatting**

A helper on the `base` model (`_get_assigned_extra_field_value`) converts field
values into display-ready data by using translated field labels and formatting
for relational values, datetimes, and monetary amounts.

**Partner-specific data provider**

`res.partner` implements `_get_assigned_extra_values` and currently contributes
email, creator, and creation date when available.

**Email template integration**

The module defines a reusable QWeb snippet and injects it into
`mail_qweb.message_user_assigned` and `mail_qweb.message_activity_assigned`
through inherited templates.
