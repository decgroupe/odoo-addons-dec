This module extends stock traceability so replenishment activity created from
reordering rules is visible directly from stock moves.

- It links stock moves to manufacturing orders created from matching
  reordering rules.
- It links stock moves to purchase order lines created from matching
  reordering rules.
- It adds those linked documents to the traceability status and the
  "created items" action so users can open related records quickly.

## Technical details

**Reordering-rule links on stock moves**

The module extends stock.move with computed many2many fields that resolve
related records from stock.warehouse.orderpoint. The compute method targets
confirmed make_to_stock moves, finds matching reordering rules by product,
then searches mrp.production on orderpoint_id and purchase.order.line on
orderpoint_ids.

**Traceability integration**

The module extends _get_mts_status() to append active manufacturing and
purchase entries in the traceability status output, and extends
_get_mto_created_items() so the existing "view created item" workflow can open
the linked record generated from reordering rules.

**Orderpoint display helper**

The module adds get_head_desc() on stock.warehouse.orderpoint to build a short
header and threshold summary used in status rendering.

**Product template relation**

The module adds orderpoint_ids on product.template for direct one2many access
to linked stock.warehouse.orderpoint records.
