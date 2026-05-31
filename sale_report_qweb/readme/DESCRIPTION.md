This module customizes the quotation and sale order PDF report labels to make tax scope explicit for users.

- It renames key column and subtotal labels to clarify when values are tax-excluded.
- It updates the report total wording to clarify that the final amount is tax-included.
- It keeps the layout close to the standard report while improving readability for fiscal communication.

## Technical details

**Sale order table headers**

The module inherits sale.report_saleorder_document and replaces the main table header row to adjust labels such as Unit Price, Discount, Taxes, and line subtotal wording.

**Section subtotal row**

The module overrides the section subtotal strong label in the main sale report tbody to distinguish tax-excluded and tax-included contexts.

**Tax totals block**

The module inherits sale.document_tax_totals and replaces the subtotal and total labels in the totals table to show Subtotal (Tax-Excluded) and Total (Tax-Included).
