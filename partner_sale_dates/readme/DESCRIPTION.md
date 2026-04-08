This module enriches the partner form and list views with key sales date
information and a shipping orders smart button.

- **Last Quotation Date**: date of the most recent draft or sent sale order
  for the partner.
- **Last Sale Date**: date of the most recent confirmed sale order for the
  partner.
- **Last Sale Delivery Date**: date of the most recent effective delivery
  shipped to the partner (based on the `effective_last_date` field provided
  by `sale_delivery_last_date`).
- **Shipping Sales Button**: stat button showing how many sale orders use
  the partner as the shipping address, with a direct link to that list.

## Technical details

**Computed date fields**

`last_quotation_date`, `last_sale_date`, and `last_sale_delivery_date` are
stored computed fields on `res.partner`. They are recomputed whenever the
related sale orders change state or date. Each relies on a `search()` query
with `child_of` to account for partner hierarchies.

**Shipping count field**

`shipping_sale_order_count` uses `_read_group` on `sale.order` grouped by
`partner_shipping_id` and walks the partner hierarchy to aggregate counts
correctly. The companion `One2many` field `shipping_sale_order_ids` provides
the dependency for the `effective_last_date` compute trigger.

**View changes**

The module extends `base.view_partner_tree` (list) to add the three date
fields with the `remaining_days` widget, and extends
`sale.res_partner_view_buttons` (form) to insert the shipping stat button and
the date fields inside the `sale` group — all restricted to users in
`sales_team.group_sale_salesman`.
