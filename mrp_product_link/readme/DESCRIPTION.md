Removes the built-in 1-year date restriction from manufacturing order counts
and links on products.

- The *Manufactured* quantity shown on a product now counts **all** manufacturing
  orders regardless of their date, instead of only those started within the last
  365 days.
- The *Manufacturing Orders* smart button and the related list view show **all**
  manufacturing orders (any state, any date) instead of only *done* orders from
  the last year.

## Technical details

**`product.product._compute_mrp_product_qty`**

Replaces the parent implementation to query `mrp.production` without the
`state = done` condition and without the `date_start > 365 days` filter, so
every manufacturing order targeting the product is counted.

**`product.product.action_view_mos`**

Overrides the action domain to remove the `('state', '=', 'done')` constraint,
making the linked view show all manufacturing orders for the product variant.

**`product.template.action_view_mos`**

Same override at template level, and also resets `search_default_filter_plan_date`
to `0` so the default date filter is not applied in the resulting list view.
