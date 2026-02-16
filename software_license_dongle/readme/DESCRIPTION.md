This module adds dongle-aware licensing on top of the software license flow.

- Each software application can define a dongle product ID used during license handling.
- Activating a license with a public dongle code stores the matching private dongle identifier on the hardware record.
- Exported hardware data keeps the dongle identifier so external systems can validate or reuse it.
- Switching an application to the `other` type clears the dongle-specific product ID.

## Technical details

**Application configuration**

The module extends `software.application` with `dongle_product_id`. Its `write()` override resets that field to `0` whenever the application type becomes `other`, so only in-house applications keep dongle metadata.

**License activation**

The module extends `software.license` with a stored related `dongle_product_id` field and overrides `_prepare_hardware_activation_vals()`. During activation it decodes the public hardware identifier through `software.license.hardware.get_dongle_identifier()` and stores the result as `dongle_identifier` when the decoded value is valid.

**Hardware identifiers**

The module extends `software.license.hardware` with the `dongle_identifier` field, updates the display name in `onchange_dongle_identifier()`, converts private identifiers to public codes with a TEA-based cipher in `get_public_dongle_identifier()`, decodes them back in `get_dongle_identifier()`, and adds the dongle identifier to `_prepare_export_vals()`.
