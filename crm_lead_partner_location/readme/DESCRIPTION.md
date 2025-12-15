This module improves CRM opportunities by adding delivery contact and location
information directly on leads, so sales teams can qualify and quote using the
real shipping destination.

- Add a dedicated Delivery Address on opportunities.
- Show delivery ZIP and country details in list, form, kanban, and quick-create
  views.
- Add search and group-by capabilities for delivery address and delivery ZIP.
- Keep delivery address continuity when creating quotations from opportunities.

## Technical details

**crm.lead model extension**

The module adds `partner_shipping_id` on `crm.lead` plus related stored fields
for delivery country/city/ZIP (`partner_shipping_country_id`,
`partner_shipping_city_id`, `partner_shipping_zip_id`). It also adds related
partner location fields (`partner_city_id`, `partner_zip_id`).

The `_onchange_partner_id` override sets `partner_shipping_id` to the default
delivery address of the selected customer. The `_convert_opportunity_data`
override injects `partner_shipping_id` into converted opportunity values so
shipping data is preserved when an opportunity is converted.

**res.partner address resolution override**

The `res.partner.address_get` override checks `default_opportunity_id` in
context and, when present with a lead-specific delivery address, forces the
`delivery` address result to that lead shipping partner. This ensures downstream
flows use the shipping contact selected on the opportunity.

**sale.order default values override**

The `sale.order.default_get` override reads `opportunity_id` defaults and sets
`partner_shipping_id` from the linked lead when available, improving quotation
defaults for CRM-generated sales orders.

**CRM views**

The module extends CRM opportunity list/form/search/kanban/quick-create views
to expose delivery address and ZIP fields in UI and filtering/grouping options.
