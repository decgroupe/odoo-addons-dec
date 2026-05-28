This module adds a full execution trace for product pricelist computation.

- records each decision made while selecting and applying pricelist rules.
- keeps a readable step-by-step history for debugging complex pricing chains.
- builds Mermaid graph data so the pricing flow can be visualized.

## Technical details

**Pricelist computation trace**

The module extends `product.pricelist` and wraps `_compute_price_rule`.
When the `history` context is enabled, it stores ordered trace entries and
graph nodes/edges for each `(product, quantity, uom)` key.

**Rule applicability trace**

The module extends `product.pricelist.item` and instruments
`_is_applicable_for` to log why a rule is skipped (minimum quantity,
category mismatch, template or variant mismatch).

**Price formula trace**

The module instruments `_compute_price` and `_compute_base_price` to track
base price origin and formula steps (discount, rounding, surcharge, min/max
margin), including nested calls when a rule is based on another pricelist.
