This module bridges the `sale_traceability` and `sale_purchase` modules to
show related purchase order lines directly on the sale order line form view.

- When a service product is bought to fulfil a sale order line (via the
  `sale_purchase` flow), the generated purchase lines are listed inside
  the traceability section of that sale order line.

## Technical details

**Purchase line display**

Overrides the inherited `sale_traceability.sale_order_form_view` view by
adding a `purchases` div inside the `traceability_container` div. The div
is restricted to users that belong to the
`group_sale_purchase_traceability` security group and is hidden when the
`purchase_line_ids` field is empty or when the line has a `display_type`
(section/note lines).
