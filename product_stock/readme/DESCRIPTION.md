This module adds a small stock history view on products.

- Last stock move: quickly see the latest non-draft stock move for each product.
- Last inventory: see the latest inventory count, its date, and the counted quantity.
- Inventory checks: find products that were inventoried at a given location or still need an update.

## Technical details

**Latest stock move**

`product.product` gets a computed `last_move_id` and `last_move_date`.
The implementation searches non-draft `stock.move` records ordered by date and
keeps the newest move for each product.

**Latest inventory**

`product.product` also gets computed inventory fields backed by `stock.quant`.
The code looks at quants in the main stock location, uses their last inventory
date to find the latest counted quant per product, and exposes the quant record,
its date, and its current quantity.

**Inventory lookups**

The search helpers use ORM queries on `stock.quant` and `stock.move` instead of
the removed 14.0 inventory model. They stay aligned with the stock location used
by the main inventory fields.
