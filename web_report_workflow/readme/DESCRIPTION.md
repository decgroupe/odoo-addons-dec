This module improves the standard PDF report layout for business documents.

- Shows a compact company contact block in the header with postal address, phone, mobile, and email.
- Adds a clearer footer with company legal and accounting details (VAT, SIRET, APE, and bank footer).
- Keeps pagination visible on PDF reports and displays the document name when footer display is enabled.
- Applies dedicated SCSS styling to report rendering through the common report asset bundle.

## Technical details

**External layout override**

The module inherits `web.external_layout_standard` and applies `xpath` replacements with `priority="99"` to:

- replace the `company_address` block with a custom contact rendering based on `company.partner_id`.
- replace the footer container and inject `company.report_footer`, `company.vat`, `company.siret`, `company.ape`, and `company.report_bank_footer`.
- keep PDF page numbering and optional `display_name_in_footer` behavior in the customized footer.

**Report styling**

The stylesheet `web_report_workflow/static/src/css/style.scss` is loaded through the manifest `assets` section under `web.report_assets_common`.

