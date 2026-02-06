This module simplifies expense entry by allowing users to fill expense lines
directly inline within the expense sheet form view, without having to open each
expense record individually.

- **Inline editing**: expense lines can be created, edited, and deleted directly
  in the sheet's list, with pre-configured columns such as amount (tax included),
  VAT, comments, and attachments.
- **Manual VAT override**: each expense line exposes a manual tax amount field,
  letting users override the automatically computed tax without changing the
  total price.
- **Automatic sheet name**: new expense sheets are pre-named according to the
  billing period (e.g. `2025/11-November`), derived from the current date minus
  10 days so that expenses filed in the first days of a month are attributed to
  the previous period.
- **Duplicate expense action**: a one-click duplicate button on each expense line
  copies the expense into the same sheet.

## Technical details

**Inline editing in the sheet form**

The `expense_line_ids` list widget is customised to remove the custom widget and
enable `editable="bottom"`. Several column attributes are adjusted (optional
visibility, force-save, relabelling).

**Manual tax amount**

`hr.expense` gains two computed fields: `manual_tax_amount` (stored, editable)
and `automatic_tax_amount` (non-stored). When `manual_tax_amount` differs from
the ORM-computed `tax_amount`, `automatic_tax_amount` is `False`, and
`_compute_tax_amount_currency` uses the manual value instead of the computed
one. The method also validates that all applied taxes have `price_include = True`
and raises a `UserError` otherwise.

`hr.expense.sheet._compute_amount` is overridden to aggregate tax amounts
correctly: it sums `tax_amount` for automatic lines and `manual_tax_amount` for
manually overridden lines.

**Price unit behaviour**

`_compute_from_product` always forces `product_has_cost = True`, and
`_needs_product_price_computation` always returns `False`, so the `price_unit`
is always derived from the user-entered `total_amount` rather than the product
catalogue cost.

**Automatic sheet name**

`hr.expense.sheet._get_default_name` computes a period-aware name: it takes
`today - 10 days` to determine the billing month, then formats it as
`YYYY/MM-MonthName`.
