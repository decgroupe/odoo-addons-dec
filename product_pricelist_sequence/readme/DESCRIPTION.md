This module gives you full control over which pricelist rule is applied first.

- Adds a dedicated sequence on pricelist lines so you can define rule priority
  explicitly.
- Adds a rule name field to make each pricing rule easier to identify.
- Improves the pricelist lines view with extra columns that help users review
  rule scope and behavior.

## Technical details

**Rule ordering and labeling**

The module extends `product.pricelist.item` and sets a custom `_order`
(`sequence, applied_on, min_quantity desc, categ_id desc, id desc`) so the
lowest sequence is evaluated first. It adds two fields: `sequence`
(`fields.Integer`, default `5`) and `note` (`fields.Char`, displayed as rule
name).

**Computed display name**

The `_compute_name` method is extended. When `note` is set, the computed name
is prefixed with the rule name to improve readability in views and selections.

**View inheritance**

The module inherits product pricelist item tree and form views to expose
`sequence` and `note`, and inherits the pricelist form to enrich the rules list
with additional columns such as `product_tmpl_id`, `product_id`, and `categ_id`.
