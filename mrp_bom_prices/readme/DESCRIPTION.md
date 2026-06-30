This module adds cost and public pricing information to BoM lines and
BoMs, making it easy to see component costs and suggested public prices
directly on manufacturing bills of materials.

- Adds `cost_price`, `unit_price` and `public_price` on `mrp.bom.line`.
- Adds `cost_price` on `mrp.bom` as the summed cost of its lines.
- Uses supplier list price when a seller is set, otherwise falls back to
	the product's standard cost; unit prices are converted using the
	component and BoM line units of measure.

## Technical details

**Models extended**

- `mrp.bom` — adds a computed `cost_price` field. The value is computed in
	`models/mrp_bom.py` by summing the `cost_price` of the BoM lines.
- `mrp.bom.line` — adds computed fields `unit_price`, `cost_price` and
	`public_price` implemented in `models/mrp_bom_line.py`.

**Computation rules**

- When a BoM line has a `seller_id`, the module uses the seller's
	`list_price_unit` as the base price; otherwise it uses
	`product.standard_price` as the cost source.
- `unit_price` is converted from the source price to the BoM line's UoM
	using the product UoM conversion helpers.
- `cost_price` on the line equals `unit_price * product_qty`.
- `public_price` is computed from `product.lst_price` and converted to the
	BoM line UoM.

**Views**

- The module injects the three price fields into the BoM form and BoM line
	form views (`views/mrp_bom.xml`) so totals and per-line prices are visible
	during editing. The BoM view displays a monetary total for `cost_price`.

**Dependencies**

- Declared in the manifest: `mrp`, `mrp_bom_supplier`, and `product_prices`.

Files of interest: `models/mrp_bom.py`, `models/mrp_bom_line.py`, and
`views/mrp_bom.xml`.
