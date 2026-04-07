This module configures the `hr_expense_easy` module for use with a French chart
of accounts. After installation it automatically assigns the correct French
accounting account codes and supplier VAT taxes to each expense category and
product defined by `hr_expense_easy`.

- Expense categories (transport, catering, lodging, other) each receive the
  appropriate French general ledger account.
- Expense products (plane, train, hotel, restaurant, …) each receive an expense
  account and, where applicable, the matching French purchase VAT tax (20%, 10%,
  5.5%, or 2.1%).

## Technical details

**Post-install hook**

All assignments are performed inside `post_init_hook` in `hooks.py`. The hook
resolves company-specific account.tax records using the XML ID pattern
`account.{company_id}_{tax_xmlid}` introduced in Odoo 17 to replace the
old company-1-hardcoded `l10n_fr.1_{tax_xmlid}` references. Any missing
account code or VAT tax reference is silently skipped with a warning in the log,
so the hook is safe to run even on a database where the French chart of accounts
has not been fully deployed.
