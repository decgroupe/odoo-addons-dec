This module adds a **main public category** concept for website products, making
it easier to classify and search products by their primary eCommerce category.

- Adds a `Website Main Product Category` field on product templates, automatically
  computed as the first entry of the existing `public_categ_ids` many2many field.
- Exposes a `set_main_public_category` method on both `product.template` and
  `product.product` to programmatically change the main category while keeping
  the other categories intact.
- Adds a search field and a group-by filter for the main category in the backend
  website product search view.

## Technical details

**Main category field**

`product.template` is extended with a stored computed Many2one field
`public_categ_id` that always reflects `public_categ_ids[0]`. It is recomputed
whenever `public_categ_ids` changes.

**set_main_public_category**

Both `product.template` and `product.product` expose this helper method. It
replaces the first category in `public_categ_ids` with the given `categ_id`
while preserving all other categories (from index 1 onward) and deduplicating
the new value if it was already present elsewhere in the list.
`product.product.set_main_public_category` simply delegates to the underlying
template via `mapped("product_tmpl_id")`.
