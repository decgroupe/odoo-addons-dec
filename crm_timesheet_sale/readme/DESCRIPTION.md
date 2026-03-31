Allows linking timesheet entries to sale orders via CRM opportunities.

- when a timesheet entry has an opportunity assigned, a **Sale Order** field
  appears to let the user associate the entry with a specific sale order linked
  to that opportunity.
- on the CRM opportunity form, a **Sales** tab lists all sale orders linked to
  the opportunity.

## Technical details

**`account.analytic.line` — `sale_id` field**

A `Many2one` field pointing to `sale.order` is added to `account.analytic.line`.
The field is only visible in the timesheet form view when `lead_id` is set
(`invisible="not lead_id"`). The domain restricts selectable orders to those
whose `opportunity_id` matches the current `lead_id`.

**CRM opportunity form**

The view inherits `sale_crm.crm_case_form_view_oppor` to insert a *Sales* page
before the *Extra Information* tab, showing `order_ids` with a
`many2many` widget.
