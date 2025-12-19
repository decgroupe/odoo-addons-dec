This module adds clear "To Invoice" amounts on sales orders and quotations,
based on ordered quantities.

- Shows untaxed and taxed amounts still to invoice on sales order lines.
- Adds the same "To Invoice" values on sales order and quotation list views.
- Adds an invoicing progress rate on the sales order list.
- Extends the tax totals widget in the sales order form to display both values.

## Technical details

**Order line computation**

The module extends `sale.order.line` with stored computed monetary fields
`amount_to_invoice_ordqty_taxexcl` and `amount_to_invoice_ordqty_taxincl`.
The compute method recalculates invoiceable amounts from ordered quantity and
already invoiced lines, including currency conversion and tax recomputation.

**Order aggregation and rate**

The module extends `sale.order` with aggregated stored computed fields for the
same untaxed/taxed values and an `invoicing_rate` float. Aggregation is done
with `read_group` on lines, and the rate is derived from
`amount_total - amount_to_invoice_ordqty_taxincl`.

**Tax totals and UI integration**

`_compute_tax_totals` is extended to inject both computed values into
`tax_totals`. XML inherited views add fields in the order line list, sale/quote
tree views, and a progress bar column. An OWL template extension of
`account.TaxTotalsField` renders dedicated rows for both "To Invoice" amounts.
