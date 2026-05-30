This module improves stock picking follow-up by reusing "My Activities" behavior
directly on transfer records.

- Stock transfers are integrated with the personal activity workflow so users can
	focus on their own pending actions.
- The transfer list keeps a highlighted name and shows the scheduled date with a
	remaining-days widget to make planning easier.

## Technical details

**Activity integration on stock pickings**

The module extends `stock.picking` with `mail.activity.my.mixin` in
`models/stock_picking.py`, enabling user-scoped activity behavior inherited from
the `mail_activity_my` dependency.

**List view adjustments**

The inherited view `stock_activity_my.vpicktree` updates the stock picking list
arch by setting `decoration-bf="1"` on the `name` field and
`widget="remaining_days"` on `scheduled_date`.
