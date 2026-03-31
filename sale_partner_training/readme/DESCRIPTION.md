This module links educational training specialties to sale orders.

- **Training specialties on orders**: a `Specialties` many2many field is added
  to sale orders, allowing users to associate one or more educational training
  specialties with each order.
- **Filter by specialty**: the sale order search view is extended so orders can
  be filtered by training specialty.

## Technical details

**Training specialties field**

`sale.order` is extended with a `training_specialty_ids` Many2many field
pointing to `res.partner.training.specialty` (defined by the `partner_training`
module). The field is surfaced in the sale order form view (before
`partner_id`) and in the search/filter sidebar.
