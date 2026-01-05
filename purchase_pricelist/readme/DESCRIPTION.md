This module extends the standard pricelist model so the same pricing engine can
be used for both Sales and Purchases.

- Adds a dedicated Purchase Pricelist on vendors and purchase orders.
- Keeps sale and purchase pricelists separated with explicit type filters.
- Uses purchase pricelist rules to compute purchase order line prices.
- Exposes supplier list prices computed from matching purchase pricelist rules.

## Technical details

**Pricelist model split**

The module extends product.pricelist with a type selection containing sale and
purchase values. It keeps the standard sale lookup on sale flows and adds a
parallel purchase lookup method used by partner purchase pricelist computation.

**Partner purchase pricelist property**

The module adds property_product_pricelist_purchase and
specific_property_product_pricelist_purchase on res.partner. The compute and
inverse logic mirrors sale behavior while storing a company-specific explicit
value and supporting fallback lookup for country and generic defaults.

**Purchase order integration**

On purchase.order, a stored editable pricelist_id field is added with a domain
restricted to purchase-type pricelists. When the pricelist changes, all lines
are recomputed so unit price and planned date follow the selected purchase
pricelist context.

**Purchase order line pricing**

The module overrides _compute_price_unit_and_date_planned_and_name on
purchase.order.line. For lines on orders with a purchase pricelist, it computes
the unit price through _get_product_price and then applies tax-included price
normalization. Non-managed lines still use the parent implementation.

**Supplier info computed list prices**

On product.supplierinfo, list_price and list_price_unit are computed fields that
derive prices from the vendor purchase pricelist rule when a rule matches,
otherwise they fall back to converted supplier price.

**Seller selection ordering**

The module adjusts product.product._prepare_sellers sorting to prioritize higher
minimum quantities first, keeping sequence as a tiebreaker.
