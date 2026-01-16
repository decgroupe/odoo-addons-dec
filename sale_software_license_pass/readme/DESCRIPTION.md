This module links software license passes with sales so passes are generated and tracked directly from Sales Orders.

- Products can be configured to create an application pass when sold.
- Confirming a sales order creates the related pass automatically.
- Cancelling a sales order cancels draft passes or creates a warning activity on non-draft passes.
- Sales users can open related passes from the sales order smart button.
- Delivered quantity for pass products is computed from sent passes.

## Technical details

**Pass generation from sales lines**

The module extends sale order lines with the `application_pass` delivered method.
On sale order confirmation (`sale.order._action_confirm`), lines marked as
application pass products call `_application_pass_generation`, which creates a
`software.license.pass` and synchronizes it with its pack.

**Product and pack binding**

It adds `license_pack_id` on product variants and a writable related field on
product templates. A new `service_tracking` option (`create_application_pass`)
activates pass generation and keeps pack selection consistent through onchange
logic.

**Sales order integration**

The module adds pass links on sales orders (`license_pass_ids`) and a stat
button in the form view. It also updates pass values when ordered quantities
change and computes delivered quantities according to the pass unit category.

**Cancellation and project overview behavior**

On sale cancellation, draft passes are cancelled and a message is posted;
non-draft passes receive a scheduled warning activity. The project overview
table helper is also adjusted to exclude sale order lines already linked to
passes.
