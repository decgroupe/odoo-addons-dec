This module bridges the `tagging` and `product_reference` modules, allowing
tags to be assigned to product references and attributes.

- References (`ref.reference`): can be tagged to group or categorize them.
- Attributes (`ref.attribute`): can also receive tags for easier filtering.
- Tags (`tagging.tags`): show linked references and attributes in their form
  view.

## Technical details

**Many2many between `ref.reference` and `tagging.tags`**

Implemented by extending `ref.reference` with a `tagging_ids` field
(Many2many → `tagging.tags`, relation table `tagging_ref_reference`) and the
inverse `reference_ids` field on `tagging.tags`.

**Many2many between `ref.attribute` and `tagging.tags`**

Implemented by extending `ref.attribute` with a `tagging_ids` field
(Many2many → `tagging.tags`, relation table `tagging_ref_attribute`) and the
inverse `attribute_ids` field on `tagging.tags`.

**View extension**

A "References" page is added to the `tagging.tags` form view, listing the
linked `reference_ids` and `attribute_ids` records.
