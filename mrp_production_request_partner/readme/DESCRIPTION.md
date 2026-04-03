This module enriches manufacturing production requests with partner information
automatically inferred from the linked sale order.

- **Partner**: adds a `Partner` field on production requests, automatically
  populated from the sale order's shipping address when the request is created.
- **ZIP Location**: adds a read-only `ZIP Location` field (from the partner's
  ZIP) for quick geographic reference.
- **Manufacturing order**: the partner is propagated to the manufacturing order
  when created from a production request via the wizard.
- **Views**: partner and ZIP are visible in the form, list, and search views
  of production requests, including group-by filters.

## Technical details

**Auto-fill on create**

`mrp.production.request.create()` is overridden with `@api.model_create_multi`.
After calling `super()`, if `sale_order_id` is set on the new record (populated
by the `sale_mrp_production_request_link` dependency), `partner_id` is set to
`sale_order_id.partner_shipping_id`.

**Manufacturing order propagation**

`mrp.production.request.create.mo._prepare_manufacturing_order()` is overridden
to inject `partner_id` from the production request into the values dict passed
to `mrp.production.create()`.
