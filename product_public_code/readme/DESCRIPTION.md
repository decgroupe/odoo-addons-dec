This module adds a public commercial code on products and uses it where
customers or sales users need a cleaner reference than the internal code.

- Adds a dedicated Public Code field on product templates and variants.
- Makes the public code searchable from sale order product selectors when the
	sales views enable that context.
- Shows the public code in sale order line descriptions so commercial documents
	can expose a customer-facing identifier.
- Adds product search filters and list/form fields so users can manage the code
	directly from the product screens.

## Technical details

**Product fields**

The module extends `product.product` with a `public_code` field and extends
`product.template` with a stored computed `public_code` that mirrors the single
variant value when a template has only one variant.

**Search integration**

The `name_search()` methods of `product.product` and `product.template` are
overridden to append matches on `public_code` when the `search_public_code`
context key is enabled. A leading `*` clears the usual domain so the public
code lookup can ignore constraints such as `sale_ok`.

**Sales behavior**

The sale order form view injects the `search_public_code` context on product
selectors. An onchange on `sale.order.line.product_id` rewrites the line label
to use `[public_code] product_name`, keeping the existing multiline description
after the first line.

**Views**

Inherited product template, product variant, and sale order views insert the
Public Code field in form/list/search views and add a "Has a Public Code"
search filter on product templates.
