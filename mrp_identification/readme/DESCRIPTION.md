This module improves how manufacturing records are identified and searched.

- Makes manufacturing orders easier to find by allowing search on BOM code,
	product internal reference, product name, and partner location.
- Enriches manufacturing order labels in search results with contextual
	identification details.
- Improves Bill of Materials labels by showing BOM code together with the
	related product information.

## Technical details

**mrp.production search behavior**

The module overrides `name_search` on `mrp.production` to clean incoming labels
before searching and to add a fallback search domain on `partner_zip_id`,
`bom_id.code`, `product_id.default_code`, and `product_id.name` when the
default search returns no result.

**mrp.production display label**

The module overrides `_compute_display_name` on `mrp.production` and, in
`name_search` context, appends identification fragments returned by
`_get_name_identifications()` (BOM label, partner label, and partner location)
to produce a richer display name.

**mrp.bom display label**

The module overrides `_compute_display_name` on `mrp.bom` to prefix the BOM
code and keep the product name visible, which helps disambiguate similar BOMs.
