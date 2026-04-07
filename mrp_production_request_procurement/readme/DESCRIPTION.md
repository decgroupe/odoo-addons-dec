This module extends Manufacturing Requests to assign a shared procurement
group across all Manufacturing Orders created from the same request.

- **Common procurement group**: when enabled, a single `procurement.group`
  is created on approval and reused for every MO generated from the request.
- **Consistent MO naming**: MOs are named after the request's production
  prefix (e.g. `WH/MO/00042`). When more than one MO is created, an
  indexed suffix is appended (e.g. `WH/MO/00042/01`, `WH/MO/00042/02`).

## Technical details

**Common procurement group**

The `mrp.production.request` model gets two new fields:
`use_common_procurement_group` (boolean) and
`common_procurement_group_id` (Many2one to `procurement.group`).
When `button_approved()` is called and the flag is set, a
`procurement.group` is created and stored on the request.

**MO naming**

`_create_sequence()` is overridden to capture the next value from the
operation type's sequence and store it in `production_name`. The request
`name` is derived from it by replacing the `MO` prefix with `MR`.

The wizard `_prepare_manufacturing_order()` is overridden to:

1. Assign `common_procurement_group_id` as the MO procurement group when
   the flag is active, or clear it otherwise (avoids side-effects from
   reusing an unrelated group).
2. Build the MO name: bare `production_name` for single-quantity requests,
   or `production_name/NN` for multi-quantity / repeated MO creation.
