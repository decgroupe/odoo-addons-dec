This module allows storing and managing software service accounts linked to
suppliers, products, manufacturing orders, and partners.

- **Account management**: store login, password, e-mail, security question/answer,
  PIN and free-text notes for each account.
- **Supplier classification**: group accounts by supplier (e.g. Google, Steam)
  with an optional image for easy visual identification.
- **Traceability**: each account can be linked to a product, a manufacturing
  order, and a partner for full traceability.

## Technical details

**software.account.supplier**

A simple master-data model holding the supplier name, an optional binary image,
and free-text rules for credential management.

**software.account**

Stores credentials and metadata for a software service account. Relations to
`product.product`, `mrp.production`, and `res.partner` are optional Many2one
fields that allow linking the account to a specific product, manufacturing run,
or customer/vendor.
