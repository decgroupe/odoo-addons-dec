This module adjusts how the cost price is sourced on sale order lines, ensuring
the margin computation reflects the actual purchase price from your supplier
pricelists rather than the product's internal cost.

- **Purchase price on sale lines**: instead of using `standard_price`, the cost
  field on each sale order line is populated from `default_purchase_price`
  (computed by `product_prices` from the main supplier's pricelist).
- **Extensible hook**: a `_get_purchase_price()` method is exposed on
  `sale.order.line` so downstream modules can override the cost source without
  duplicating the currency conversion logic.

## Technical details

**Cost source override**

`SaleOrderLine._compute_purchase_price` is overridden to call
`_get_purchase_price()` (which returns `product_id.default_purchase_price`)
instead of reading `product_id.standard_price` directly. The result is then
converted to the sale order currency using `_convert_to_sol_currency` (available
since Odoo 18.0 in `sale.order.line`), and UoM conversion is applied when the
line UoM differs from the product's default UoM.

**Extensible hook**

`_get_purchase_price()` is designed to be overridden by modules that need a
different cost source (e.g. a project-specific cost or a negotiated frame price).
