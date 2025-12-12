This module exposes up to three analytic hierarchy levels directly on analytic
entries.

- It adds primary, secondary, and tertiary analytic account fields on analytic
	lines.
- It helps users filter, group, and report entries by parent analytic levels
	without manually traversing the account hierarchy.

## Technical details

**Analytic line extension**

The module extends `account.analytic.line` and adds three stored computed
Many2one fields: `account_primary_id`, `account_secondary_id`, and
`account_tertiary_id`.

**Hierarchy computation**

The `_compute_analytic_account_level` method walks up `account_id.parent_id` to
build the account chain from root to leaf, then maps the first three positions
to the new fields.

**Missing levels handling**

When fewer than three hierarchy levels exist, the compute method explicitly
fills remaining positions with `False`, so obsolete values are always cleared.
