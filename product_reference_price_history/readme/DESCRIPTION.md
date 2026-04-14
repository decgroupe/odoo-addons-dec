This module tracks the material cost price history for product references
(`ref.reference`). Each time the computed BOM cost changes for a reference, a
new `ref.price` record is stored so that cost evolution can be audited over
time.

Key features:

- A scheduled action runs nightly to recompute BOM costs for all active
  references and records a new price entry whenever the cost has changed.
- References with the **ADT** category are excluded from the computation.
- A reporting wizard lets users generate an HTML email summarising all
  references whose latest computed cost is higher than the previous one.
- The report can be filtered by a custom date range or sent immediately with
  all price increases detected in the last 24 hours.
- Recipients are configurable via a system parameter
  (`product_reference_price_history.cost_report_email`) and the wizard's
  *To (Emails)* field.

## Technical details

- Extends `ref.reference` (from the `product_reference` module) with a
  `price_ids` One2many linking to the new `ref.price` model.
- BOM cost computation uses `mrp.bom._bom_find` and reads the `cost_price`
  field provided by the `mrp_bom_prices` module.
- Email rendering relies on a Jinja2 `mail.template` record; all report data
  is passed through the rendering context rather than via the template record
  object.
- The `reference.compute_material_cost` and
  `reference.generate_material_cost_report` transient models (both inheriting
  `wizard.run`) expose the scheduler and report generator from the UI.
