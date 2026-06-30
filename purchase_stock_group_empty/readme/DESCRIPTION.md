This module ensures procurements that don't belong to any procurement
group are pooled together instead of creating separate purchase orders.

- Groups procurements that have no `group_id`, so they are considered
	together when searching for an existing purchase order to reuse.
- Prevents mixing grouped and ungrouped procurements in the same PO.

## Technical details

The module inherits `stock.rule` and overrides the `_make_po_get_domain`
method. When the original domain does not explicitly set `group_id`, the
method forces the PO search domain to include `('group_id', '=', False)`.
This restricts candidate purchase orders to those without a procurement
group and therefore groups ungrouped procurements together.

The implementation lives in `models/stock_rule.py` and only adjusts the PO
search domain — it does not change the purchase order creation flow itself.
