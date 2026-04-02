This module provides legacy compatibility fields and data for the Software
License module. It maps legacy VR system types (Classic, Cave, Rift, Vive) to
structured feature flags, and exposes the primary hardware identifier directly
on the license record.

- **System type flags**: boolean fields (`system_classic`, `system_cave`,
  `system_rift`, `system_vive`) are automatically computed from the linked
  feature entries. They can also be set directly at license creation to
  auto-create the corresponding feature record.
- **Main hardware shortcut**: a `main_hardware_id` computed field points to the
  first linked hardware device, with related fields for its identifier and
  dongle ID exposed directly on the license.

## Technical details

**System type flags**

`_compute_system` iterates over `feature_ids` and sets the four boolean fields
by matching the linked `software.license.feature` against the four
`feature_value_system_*` records defined in this module's data. The `create`
override calls `try_create_property_value` for each system boolean present in
`vals` to create the matching feature record automatically.

**Main hardware shortcut**

`_compute_main_hardware` stores the first entry of `hardware_ids` in
`main_hardware_id`. The related fields `main_hardware_name` and
`main_hardware_dongle_identifier` are then read from that record.
