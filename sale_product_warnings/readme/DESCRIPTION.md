This module improves sales warnings when products with a risky lifecycle state
are added to quotations or confirmed orders.

- Shows a contextual popup warning on sale order lines when the selected
  product is in obsolete, review, or quotation state.
- Includes product notes and the product responsible user in warning messages
  when available.
- Schedules a review activity on the sale order when a product in review state
  is added.
- Blocks sale confirmation for products explicitly configured with a blocking
  warning policy.

## Technical details

**sale.order.line warning behavior**

The module overrides sale.order.line._onchange_product_id_warning to build a
custom warning payload depending on product_id.state. Messages are rendered with
self.env._() and include product description and responsible_id when present.

**review activity scheduling**

The module overrides sale.order.line.create. After record creation, each new
line linked to a product in review state triggers _schedule_review_activity,
which schedules mail.activity.type
sale_product_warnings.mail_activity_data_review with template
sale_product_warnings.exception_product_review.

**confirmation blocking policy**

The module extends product.template.sale_line_warn with a
block_confirm selection value. product.product._check_warn raises a
ValidationError when products configured with this warning type are detected.

**sale confirmation check trigger**

The module overrides sale.order.write to run product warning checks after write
when the order reaches confirmed state and relevant fields were changed.
