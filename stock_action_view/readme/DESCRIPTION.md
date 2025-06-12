This module adds smart navigation actions for key stock records.

- Open stock records directly from server-side code without duplicating action definitions.
- Reuse standard stock actions while automatically adapting behavior for one or many records.
- Show a list view when multiple records are selected, or jump straight to the form view when a single record is selected.

## Technical details

**Reusable base actions**

The module adds an `action_view_base()` helper on the following models:
`stock.picking`, `stock.move`, `stock.rule`, `stock.warehouse.orderpoint`, and
`procurement.group`. For stock models, the helper loads existing XML actions with
`ir.actions.actions._for_xml_id(...)`. For `procurement.group`, it builds a
minimal window action dict because no direct stock XML action is reused there.

**Context-aware action rendering**

Each model also provides `action_view()` that adapts the returned action to the
active recordset:

- no record: returns the base action as-is.
- multiple records: applies a domain `[("id", "in", self.ids)]` and keeps list then form navigation.
- single record: forces the related form view and sets `res_id` to open the target record directly.

This keeps behavior consistent across stock-related objects while avoiding
action duplication in custom code.
