This module provides an analysis-oriented view of pricelist rules so users can
inspect and manage pricing logic faster.

- From product template and product variant forms, the standard "Pricelist
	Rules" action opens a richer list of rules instead of the restrictive default
	Odoo action.
- From the pricelist form, a stat button opens all pricelist items directly.
- The pricelist item list emphasizes analysis fields such as category,
	template, price computation parameters, and grouping options.

## Technical details

**Custom action and context routing**

The module defines a dedicated window action
`product_pricelist_analysis.act_window_product_pricelist_item` and routes all
entry points to it. The methods `open_pricelist_rules()` and
`action_view_pricelist_items()` are overridden on `product.template`,
`product.product`, and `product.pricelist` to inject search defaults
(`search_default_product_tmpl_id`, `search_default_pricelist_id`) and
`default_applied_on` values adapted to each entry point.

**Pricelist item views focused on analysis**

The inherited list view `product_pricelist_item_list_view` is promoted as a
primary list view, disables inline edition, exposes key rule fields, and
reorders columns to make rule scope and price computation easier to read. A
custom search view adds filters and group-by entries for sequence, pricelist,
category, product template, and variant.

**Form improvements and navigation**

The inherited pricelist item form displays `pricelist_id` prominently, and the
inherited pricelist form adds a button in the button box to open related
pricelist items.
