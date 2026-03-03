This module manages structured product references linked to product templates.

- Build references from categories, properties, and attributes.
- Keep a version history for each reference.
- Generate and synchronize product data from the reference lifecycle.
- Improve product lookup with reference-aware search behavior.

## Technical details

**Reference core model**

The `ref.reference` model is the central object and stores the generated
reference value, search value, category, product link, version lines, and
property lines. Its `create` method creates or links a product variant,
derives the product template, initializes default state, and creates an
initial version entry when no version is provided.

**Product integration**

The module extends `product.template` with `reference_ids` and a computed
`reference_id`. It also extends product extra search logic through
`append_extra_search` and `append_reference_search` to support lookups where
users include a version marker (`V`) in the searched text.

**Category and product category synchronization**

The `ref.category` model creates a corresponding `product.category` when needed
and keeps names synchronized on write. Category lines (`ref.category.line`)
define how properties are sequenced for reference construction.

**Property and attribute validation**

`ref.property` defines a format mask (`T`, `A`, `N`) and validates values with
`validate_value`. `ref.attribute` belongs to a property and normalizes codes
through onchange validation. `ref.reference.line` enforces required attribute
or value depending on whether the property is fixed.

**Version tracking**

`ref.version` records modification metadata (name, version number, date,
author) per reference, and default logic derives the next version context when
creating entries.
