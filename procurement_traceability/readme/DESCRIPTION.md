This module adds a dedicated procurement traceability workspace in Inventory.

- It introduces a new Traceability menu with a Procurements entry under Inventory settings.
- It provides a dedicated list and form view for procurement groups.
- It shows direct links from each procurement group to related pickings, stock moves, reordering rules, and routes.
- It adds the procurement group on stock move and picking forms to make upstream traceability easier.

## Technical details

**Procurement group workspace**

The module defines new list and form views for procurement.group and exposes them
through a dedicated ir.actions.act_window action. The form includes stat buttons and
notebook pages that display related records via existing relational fields.

**Stock document traceability fields**

The module inherits stock.view_move_form and stock.view_picking_form to insert
group_id in strategic positions, so users can navigate from operational documents to
their procurement group.

**Picking operations ordering**

The module updates the move_ids_without_package list definition in the picking form
to apply a default_order by group_id then product_id, improving grouping while
reviewing operations.
