This module improves traceability between accounting journal items and their
sales origin, making it easier to track which sale orders generated which
invoice lines.

- Adds a stored **Origin** field on journal items (`account.move.line`) that
  mirrors the `invoice_origin` of the parent invoice, enabling filtering and
  grouping by source document directly in the journal entries list.
- Extends the journal items list view to display the **Product** column.
- Extends the journal items search view to filter by **Product**, **Origin**,
  and a quick **Not attached** filter (lines not linked to any purchase or sale
  order line).
- Adds a **Group by Product** option in the journal items search view.
- Extends the journal entries list view to show the **Source Document** column.
- Extends the journal entries search view to allow searching by
  **Source Document**.
- On the sale order form, the *Invoice Lines* smart button opens the journal
  items list pre-filtered by origin and product to show only the lines
  relevant to that sale order.
- Adds a **Sale Lines** tab on the journal item form (visible to salespeople)
  showing the linked sale order lines.

## Technical details

**Stored related `invoice_origin` on `account.move.line`**

`AccountMoveLine` is extended with a `Char` field `invoice_origin` that is a
stored `related` of `move_id.invoice_origin`. Storing this field allows it to
be used in domain filters, group-by contexts, and the search view without
a join, which is essential for the "Not attached" filter and the sale order
context filter.

**View extensions**

All view customisations are implemented as inherited views using `<xpath>` or
positional `<field>` insertions. No new menus or actions are added - the
module only enriches existing accounting views.
