This module adds supplier planning information directly on Bill of Materials lines.

- Select a preferred supplier on each BoM component line.
- See and edit the expected lead time used for procurement or manufacturing.
- Store an internal landmark/reference on each BoM line to improve traceability.

## Technical details

**BoM line model extension**

The module extends `mrp.bom.line` with:

- `partner_id` (`res.partner`) to select the supplier.
- `seller_id` (`product.supplierinfo`) as a computed supplier info record.
- `seller_partner_ids` as a computed domain helper for supplier choices.
- `delay` as a computed and inverse integer synchronized with supplier delay or BoM
  production delay.
- `landmark` as an additional free-text identifier.

`_compute_supplier_info` selects the matching seller with `_select_seller`,
using the selected supplier when provided, or the product main seller as
fallback.

`_compute_delay` and `_inverse_delay` handle Make To Order products and keep the
lead time consistent with either `product.supplierinfo.delay` (buy flow) or
`mrp.bom.produce_delay` (manufacture flow).

**View integration**

The module inherits both the BoM form (`mrp.mrp_bom_form_view`) and BoM line
form (`mrp.mrp_bom_line_view_form`) to insert `partner_id`, `delay`, and
`landmark` in the user interface.
