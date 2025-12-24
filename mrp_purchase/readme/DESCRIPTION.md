This module links Manufacturing Orders (MOs) with Purchase Orders (POs) to
handle service procurement and cross-cancellation notifications.

- **Service procurement**: when a Manufacturing Order is confirmed, service
  products marked as purchasable in the Bill of Materials are automatically
  procured via a purchase order. The resulting purchase order lines are linked
  back to the originating MO.
- **Traceability**: each purchase order line references the MO that generated
  it, and each MO lists all its related purchase order lines, giving full
  visibility in both directions.
- **Cancellation warnings**: cancelling a MO schedules a warning activity on
  the linked open purchase orders; cancelling a purchase order schedules a
  warning activity on the linked open MOs, so operators are always informed of
  cross-document impacts.

## Technical details

**Service procurement from BOM**

`MrpProduction._create_services` is called inside `action_confirm`. It
explodes the BOM and, for each service-type BOM line whose product has
`purchase_ok = True`, calls `_action_launch_procurement_rule` to push a
`procurement.group.Procurement` request. The procurement values carry
`production_id` and `service_bom_line_id` so the resulting purchase order
line can be linked back to the MO and to its BOM line.

**Traceability fields**

- `mrp.production.purchase_line_ids`: many2many to `purchase.order.line`
  (via `purchase_order_line_mrp_rel`), readonly, populated by the
  procurement hook.
- `purchase.order.line.production_ids`: inverse many2many on the same
  relation; `production_id` is a computed convenience field returning the
  first related MO.
- `PurchaseOrderLine._prepare_purchase_order_line_from_procurement` is
  overridden to inject `production_ids` and `bom_line_id` into the values
  dict during procurement.

**Cancellation notifications**

- `MrpProduction.action_cancel` calls `_activity_cancel_on_purchase`, which
  groups affected open purchase orders and schedules a warning activity using
  the `exception_purchase_on_mrp_cancellation` mail template.
- `PurchaseOrder.button_cancel` calls `_activity_cancel_on_production`, which
  groups affected open MOs and schedules a warning activity using the
  `exception_mrp_on_purchase_cancellation` mail template.
