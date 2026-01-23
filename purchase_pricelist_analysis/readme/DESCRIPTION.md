This module extends pricelist analysis for purchasing teams.

- It adds a dedicated Purchase Pricelist filter in the pricelist items analysis view.
- It provides a direct Pricelist items menu under Purchase.
- It shows how each supplier price is computed, with readable steps and a visual graph.

## Technical details

**Supplier price computation traceability**

The module inherits `product.supplierinfo` and adds computed fields for both step-by-step text and Mermaid graph output (`list_price_steps`, `list_price_graph`, `list_price_unit_steps`, `list_price_unit_graph`). It overrides `_compute_list_price` and `_compute_list_price_unit` to collect pricing history through context and then formats that history in `_get_graph_steps`. When no purchase pricelist is configured on the supplier partner, it appends a clear terminal message to the pricing history.

**Pricelist analysis search extension**

The module inherits `product_pricelist_analysis.product_pricelist_item_search_view` and updates the existing sale filter domain while adding a new `filter_pricelist_purchase` domain on `pricelist_id.type = purchase`.

**Purchase navigation integration**

The module adds a Purchase menu entry pointing to `product_pricelist_analysis.act_window_product_pricelist_item`, restricted to users in `purchase_pricelist.group_purchase_pricelist`.

**Supplier form/list UI extension**

The supplier info list view gets a technical field showing computation steps (visible to `base.group_no_one`), and the supplier info form view adds a Mermaid graph widget bound to `list_price_graph`.
