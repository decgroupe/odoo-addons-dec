This module lets a manufacturing user swap two manufacturing orders when the
wrong order was prioritized or assigned to the wrong customer/project context.

- Swap the commercial and planning metadata of two manufacturing orders without
	recreating them.
- Keep linked production requests aligned when both orders originate from a
	request.
- Reassign related timesheets and project links so the operational trace stays
	consistent after the swap.

## Technical details

**Wizard flow**

The transient model `mrp.swap.production` is opened from a bound action on
`mrp.production` and pre-fills `this_production_id` from `active_id`. The
`onchange_other_production_id` method builds swap lines for the two selected
manufacturing orders and any matching subproductions that share the same
finished product.

**Swap validation**

Before executing a swap, `_pre_swap_production_check` enforces identical key
fields on both manufacturing orders, ensures both or neither are linked to an
`mrp.production.request`, and verifies that timesheet/project constraints remain
valid.

**Swap execution**

`swap_production` exchanges order metadata such as origin, sale order, partner,
planning dates, note, project, and optionally finished move destinations.
`swap_production_request_content` applies the same logic to linked production
requests and updates the stock move pointing to each request when final moves
must also be swapped.

**Post-processing**

`update_timesheet_project` rewrites the related task and analytic line project
references, and `message_post_swap` writes a chatter entry on both swapped
records for traceability.
