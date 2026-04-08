This module adds market Bill of Materials (BoM) management to products,
allowing the definition of a reference market composition and labor structure
for each product variant.

- **Market BoM**: link a structured list of components and services to a
  product variant, with a configurable markup rate and material cost factor.
- **Labor time**: automatically computes the total labor hours from BoM lines
  matching configured labor services.
- **Market categories**: define and order market categories with prefix,
  description, and state (normal, obsolete, title).

## Technical details

**Market BoM (`ref.market.bom`)**

Each market BoM is linked to a `product.product` variant. The `labortime`
computed field sums the hours from BoM lines whose products match the list
returned by `get_labortime_services()`. This method returns an empty recordset
by default and is designed to be overridden in dependent modules.

**Market BoM line (`ref.market.bom.line`)**

Each line holds a product, a quantity, and a UoM. The `_convert_qty_to_hours`
method converts the quantity to hours when the line's UoM belongs to the time
category; otherwise the raw quantity is returned directly.

**Product integration**

`product.product` gets a `market_bom_ids` One2many and a `market_bom_id`
Many2one (computed, pointing to the first BoM) for easy prefetching.
`product.template` exposes both fields as related fields from its variants.
