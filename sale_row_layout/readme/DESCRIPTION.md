This module reorganizes the sale order line form into a row-based layout so key
pricing fields are easier to read and compare while editing a line.

- keeps the most important line fields aligned in compact tables.
- improves readability of quantity, unit, cost, price, discount, margin, and
  subtotal values.
- keeps section and note lines unaffected (the row layout only applies to
  regular product lines).

## Technical details

**Sale order form inheritance**

The module inherits `sale.view_order_form` and adjusts the `order_line` form
architecture. It first removes inline list editability, then injects placeholder
table structures, and finally moves existing labels/fields into those slots
using `xpath` with `position="move"`.

**Field positioning and visibility**

The row layout is rendered only when `display_type` is false (normal lines).
The discount field keeps `sale.group_discount_per_so_line` visibility at field
level, and UoM labels/fields keep `uom.group_uom` constraints.

**Styling**

The SCSS asset (`static/src/scss/style.scss`) styles headers, borders,
column widths, and spacing for the custom row tables used in the order line
form.
