This module allows users to register product templates as commercial packs
(company or manufacturer packs) through a dedicated reference management
interface.

- Pack registration: link a product template (or variant) to a pack record
  with a type (company or manufacturer).
- Automatic pack configuration: when a pack is created, the related product
  template is automatically configured with the appropriate pack settings
  (`pack_ok`, `pack_type`, `pack_component_price`, `pack_modifiable`,
  `pack_order_type`).
- Service product filter: a search filter is added to the product template
  list to exclude pack products from the service products view.

## Technical details

**Pack model (`ref.pack`)**

The `ref.pack` model links a product template (`product_id`) to a pack type
(`company` or `manufacturer`). A computed inverse field `product_variant_id`
allows selection by product variant; writing to it automatically resolves
the corresponding product template.

**Automatic pack configuration on creation**

The `create` method (decorated with `@api.model_create_multi`) inspects each
`vals` dict: if `product_variant_id` is provided instead of `product_id`, the
variant is resolved to its template before the record is saved. After creation,
`_set_product_tmpl_default_values` sets `pack_ok=True`, `pack_type='detailed'`,
`pack_component_price='ignored'`, `pack_modifiable=False`, and derives
`pack_order_type` from the product's `sale_ok` / `purchase_ok` flags.
