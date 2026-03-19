This module keeps a history of product purchase and sales prices over time.

- Stores a new history entry only when the computed default price changes.
- Tracks both purchase and sell prices per product and company.
- Lets users open a dedicated history view from products or product templates.
- Updates history automatically when stock moves are completed and when product
	prices are edited.

## Technical details

**History model**

The module defines the `product.prices.history` model to store timestamped
purchase and sell prices (`purchase_price` and `sell_price`) by product and
company.

**Price update logic**

`product.product` is extended with methods that compare the current computed
default price against the latest history record and create a new row only when
the value changed (`_update_price`, `update_purchase_price`,
`update_sell_price`).

**Automatic triggers**

- `product.product.write()` and `product.template.write()` trigger history
	recomputation when `list_price` or `standard_price` is modified.
- `stock.move._action_done()` triggers recomputation for moved products.
- A scheduler method (`scheduler_update_default_prices`) can update history in
	batch for products that already have stock moves.

**User interface**

`show_product_prices_history()` builds and returns an action with domain/context
to open filtered history entries for the selected products and price type.
