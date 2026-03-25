This module makes subcontracting and component purchasing more predictable by
using the supplier selected on each Bill of Materials line.

- choose a vendor on a BoM component line
- keep this vendor choice when procurement values are prepared from stock moves
- ensure generated purchase orders target the supplier selected on the BoM line

## Technical details

**Procurement value enrichment**

The module extends `stock.move` and overrides `_prepare_procurement_values()`.
When a move is linked to a BoM line and that line has a `partner_id`, the
method injects `supplierinfo_id` from `bom_line_id.seller_id` into the
procurement values dict.

**Purchase flow impact**

With `purchase_stock` and `mrp_bom_supplier`, the injected `supplierinfo_id`
drives supplier selection during buy procurement rules, so purchase orders are
created for the supplier explicitly chosen on the BoM line.
