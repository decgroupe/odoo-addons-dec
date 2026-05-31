This module adjusts the standard customer invoice PDF layout to make tax semantics clearer.

- Renames line and total labels to explicitly indicate tax-excluded and tax-included amounts.
- Keeps the invoice line taxes column visually centered for better readability.
- Preserves the default report structure while applying targeted wording/layout overrides.

## Technical details

**Invoice lines table overrides**

The module inherits `account.report_invoice_document` and replaces the main table header row. It updates labels such as *Unit Price (Tax-Excluded)* and keeps conditional behavior tied to `display_discount` and `report_type`.

**Invoice line tax column alignment**

The module targets the `td_taxes` node inside `account_invoice_line_accountable` and overrides its dynamic class so the rendered tax column is centered.

**Tax totals labels**

The module inherits `account.document_tax_totals` and replaces the subtotal and total captions so totals are explicitly labeled as tax-excluded and tax-included.
