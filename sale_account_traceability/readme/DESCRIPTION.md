Extends the sale order line with accounting traceability features.

- **Invoice lines visibility**: shows the related customer invoice lines directly
  on the sale order line form view, inside the traceability container, filtered
  to show only lines from customer invoices matching the same product.
- **Force invoiced**: adds a per-line toggle to mark a sale order line as fully
  invoiced regardless of quantities, useful when the remaining amount should not
  be billed.

## Technical details

**Invoice lines domain**

The `invoice_lines` Many2many field is extended with a domain that restricts
displayed lines to customer invoices (`move_type = 'out_invoice'`) and to lines
matching the same product as the sale order line (or lines without a product).

**Force invoiced per line**

Adds a `force_invoiced` Boolean field on `sale.order.line`. The
`_compute_invoice_status` method is overridden to:

- Set `invoice_status = 'no'` when the order is in draft state.
- Set `invoice_status = 'invoiced'` when the line price is zero and the parent
  order has its order-level `force_invoiced` flag set.
- Set `invoice_status = 'invoiced'` for any line with `force_invoiced = True`.

A button `action_force_invoiced` is exposed in the view to toggle the flag
directly from the sale order line form.

This feature is restricted to users with the
`sale_account_traceability.group_sale_account_traceability` security group.
