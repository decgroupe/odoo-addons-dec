This module keeps sale orders, manufacturing requests, and generated
manufacturing orders linked together.

- Each manufacturing request created from a sale order shows its source sale
	order directly on the request.
- Sale orders display a smart button that opens the related manufacturing
	requests.
- When a manufacturing order is created from a request, the sale order link is
	propagated to that manufacturing order.
- Cancelling a sale order either cancels still-pending manufacturing requests
	or creates a warning activity when manual follow-up is needed.

## Technical details

**Sale order linkage**

The module adds a `sale_order_id` field on `mrp.production.request` and fills
it during `create()`. It first resolves requests created from a sale order by
matching the request origin with the sale order name, then reuses the parent
manufacturing order link for requests generated from manufacturing routes.

**Sales-side navigation**

The `sale.order` model gets a `production_request_ids` one2many relation, a
stored counter, and a smart button calling `action_view_production_request()`
to open the related manufacturing requests.

**Cancellation handling**

When `sale.order.action_cancel()` is called, the module runs a sudoed follow-up
on linked manufacturing requests. Draft or to-approve requests without related
manufacturing orders are cancelled automatically; otherwise a mail activity is
scheduled with a dedicated warning template so the assigned user can review the
exception.

**Manufacturing order propagation**

The `mrp.production.request.create.mo` wizard is extended so
`_prepare_manufacturing_order()` copies `sale_order_id` from the request onto
the manufacturing order values.
