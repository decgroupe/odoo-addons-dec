This module adds "My Activities" indicators to sales quotations and orders so
each user quickly sees their own next actions.

- List views show the current user's activity widget and next activity deadline.
- Kanban view shows activity state progress and the current user's activity
	widget in the card footer.

## Technical details

**Model extension**

The module extends `sale.order` with `mail.activity.my.mixin` in
`models/sale_order.py`, which provides user-scoped activity fields such as
`activity_my_ids`, `activity_my_state`, and `activity_my_date_deadline`.

**View inheritance**

The module inherits sale quotation/order list views and sale order kanban view
in `views/sale_order.xml` to inject the user-scoped activity fields and
widgets (`list_activity_my`, `kanban_activity_my`, and `remaining_days`).
