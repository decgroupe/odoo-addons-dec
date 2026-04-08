This module links product reference categories to analytic accounts, enabling
automatic creation and synchronisation of income analytic accounts for each
reference category.

- **Auto-create**: when a reference category is created, an income analytic
  account is automatically created and linked to it (controlled by a company
  setting).
- **Name / code sync**: when a reference category is renamed or its code is
  changed, the linked analytic account name and code are updated accordingly.

## Technical details

**Auto-create on reference category creation**

Extends `ref.category.create` with `@api.model_create_multi`. If the company
setting `auto_create_reference_category_analytic_account` is enabled, calls
`action_create_income_analytic_account` on the newly created records. The
analytic accounts are created under the "Products" `account.analytic.plan`
(defined in `data/account_analytic_account.xml`).

**Name and code synchronisation**

Overrides `ref.category.write` to propagate name and code changes to the linked
`account.analytic.account`, but only when the analytic account name/code still
matches the previous category name/code (to preserve manual overrides).

**Company setting**

Adds `auto_create_reference_category_analytic_account` (Boolean, default True)
to `res.company` and exposes it via `res.config.settings`.
