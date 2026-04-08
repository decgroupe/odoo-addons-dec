This module adds a button on posted invoices to set or recreate the analytic
distribution on invoice lines and their corresponding journal items, based on
the analytic accounts configured on each product and product category.

- **Set Default Analytic Account**: a button on the invoice form view forces
  the analytic distribution to be recomputed from the product's income/expense
  analytic account (as configured by the `product_analytic` and
  `product_category_analytic` modules).
- **Account Invoice Update wizard integration**: extends the update wizard to
  show the product associated with each journal item line, and adds a button
  to remove all lines that have a product assigned.

## Technical details

**Set Default Analytic Account button**

`AccountMove._set_default_analytic_account` iterates over posting journal
items filtered by `product_id`. For each item it reads the analytic
distribution from the matching invoice line (falling back to
`AccountMoveLine._get_product_analytic_distribution` when no single match is
found), then writes the distribution back to the journal item and calls
`_create_analytic_lines()` to recreate the `account.analytic.line` records.

The unlink of existing analytic lines is done with `skip_analytic_sync=True`
to prevent Odoo's `_update_analytic_distribution` hook from clearing
`analytic_distribution` as a side effect.

**Account Invoice Update wizard**

`AccountInvoiceUpdate._get_matching_inv_line` delegates to
`AccountMove._get_matching_inv_line` after attempting the parent class method.
`AccountInvoiceUpdate._get_move_lines` returns all move lines of the invoice
instead of the default filtered set.
`AccountInvoiceLineUpdate.product_id` is a related field that surfaces the
product from the underlying invoice line in the wizard list.
