This module adds user-scoped activity indicators on customer invoices and vendor bills.

- In the invoice list, each user sees their own activities with a dedicated widget.
- The view highlights the next deadline for the current user's pending activity flow.

## Technical details

**Model extension**

The module extends `account.move` with `mail.activity.my.mixin` in
`models/account_invoice.py`. This injects fields such as `activity_my_ids`,
`activity_my_state`, and `activity_my_date_deadline`.

**View inheritance**

The module inherits the account invoice list view in
`views/account_invoice.xml` and inserts `activity_my_ids` with the
`list_activity_my` widget after `invoice_date_due`.
