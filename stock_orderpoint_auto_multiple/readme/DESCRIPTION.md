This module automatically sets the orderpoint Multiple value from the product
Purchase Unit of Measure.

- It keeps replenishment multiples aligned with the product purchasing unit.
- It avoids manual updates of the orderpoint multiple when purchase UoM rules
	are used.

## Technical details

**Orderpoint multiple computation**

The module extends model stock.warehouse.orderpoint and redefines qty_multiple
as a stored computed field.

The compute method depends on product_id.uom_po_id and assigns:

- qty_multiple = product_id.uom_po_id.factor_inv

As a result, when the purchase UoM changes, the orderpoint multiple is
recomputed and stored accordingly.
