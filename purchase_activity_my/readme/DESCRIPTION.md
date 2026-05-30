This module adds a personal activity view on purchase orders so each user can
focus on their own next actions directly from list and kanban screens.

- list view: adds a dedicated activity column with the custom
	`list_activity_my` widget.
- kanban view: adds personal activity indicators and progress state through
	`activity_my_ids` and `activity_my_state`.

## Technical details

**Model extension**

The module extends `purchase.order` with `mail.activity.my.mixin` in
`models/purchase_order.py`, which provides `activity_my_ids` and
`activity_my_state` fields bound to the current user context.

**List view inheritance**

The inherited purchase list view injects `activity_my_ids` before `origin`
with the `list_activity_my` widget and keeps `remaining_days` on `date_order`.

**Kanban view inheritance**

The inherited purchase kanban view declares `activity_my_ids` and
`activity_my_state`, adds a progressbar on `activity_my_state`, and replaces
the standard `activity_ids` kanban widget with `kanban_activity_my`.
