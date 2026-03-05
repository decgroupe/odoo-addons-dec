This module adds a short summary on sales quotations and sales orders so users can
identify documents faster.

- Adds a dedicated summary text field on each quotation/order.
- Displays the summary next to the order number in list views.
- Shows an editable summary area at the top of the sales order form.

## Technical details

**Model extension**

The module extends `sale.order` and adds a `summary` `fields.Char` field (max 128
characters).

**List views**

Two inherited list views (`sale.view_quotation_tree` and `sale.view_order_tree`)
insert the `summary` field right after `name`.

**Form view**

An inherited form view (`sale.view_order_form`) inserts a `div` before the notebook
and renders the `summary` field with a placeholder, making it immediately editable.
