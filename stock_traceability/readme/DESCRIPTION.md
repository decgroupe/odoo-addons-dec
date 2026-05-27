This module improves stock move traceability directly from picking operations and
stock move forms.

- It adds a procurement status column on picking operation lines so users can see
  the upstream context (MTO/MTS origin, related documents, and warnings) without
  opening each move.
- It adds quick links from operation lines to the nearest created business
  document (for example a related warning activity or downstream document).
- It enriches incoming operation lines with supplier product code and supplier
  product name when available.
- It extends move forms and move lists with extra traceability data (linked
  moves, procurement group, references) to speed up investigation.

## Technical details

**Stock move traceability computation**

The module extends stock.move with computed fields such as pick_status,
final_location, product_activity_id, and state_symbol. The pick status is built
from MTO/MTS logic, upstream/downstream links, procurement group metadata, and
reservation checks. The final location is computed recursively from destination
moves to show the end location across chained moves.

**Picking operation view enrichment**

The inherited stock.picking form view injects vendor fields
(product_supplier_code, product_supplier_name), move linkage tags
(move_orig_ids, move_dest_ids), the computed pick_status field, and an object
button that calls action_view_created_item when a linked created item exists.

**Advanced stock move views**

The module defines an intermediate base move form and several inherited move
views to expose extra traceability fields, display technical view markers for
administrators, and provide an advanced dialog action
(action_open_stock_move_form). It also adds manager-focused editable variants for
deep troubleshooting.

**Supporting model extensions**

- mail.activity is extended with state_symbol and get_head_desc() to produce
  concise status labels used in stock move traceability output.
- procurement.group is extended with get_head_desc() to display group metadata in
  traceability headers.
- product.template gets a computed type_symbol used in traceability pre-headers.
- stock.quant overrides _update_reserved_quantity to log reservation failures
  with requested quantity before re-raising the original UserError.
