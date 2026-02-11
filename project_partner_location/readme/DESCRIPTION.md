This module enriches Projects and Tasks with delivery location information.

- Shows Shipping Partner and Shipping Partner's ZIP directly on project and task screens.
- Reuses the shipping partner from the linked sale order or project when available.
- Improves filtering and grouping so users can search and analyze work by shipping partner and ZIP.

## Technical details

**Project shipping partner computation**

The module extends project.project with computed stored fields:
partner_shipping_id, partner_shipping_zip_id, and partner_shipping_country_id.
The _compute_partner_shipping_id method selects the shipping partner from the
first linked contract, then from sale_order_id, and finally falls back to a
sale.order lookup by project name.

**Task shipping partner computation**

The module extends project.task with the same computed shipping fields.
The _compute_partner_shipping_id method resolves shipping partner in this
priority order: sale_order_id.partner_shipping_id, production_id.partner_id,
then project_id.partner_shipping_id.

**Identification and view integration**

The module extends project.project._get_name_identifications to append shipping
partner display information (or partner_id as fallback), improving project
identification. It also inherits project and task form, list, kanban, and
search views to display shipping fields and extend partner search domains and
group-by options with shipping partner and ZIP values.
