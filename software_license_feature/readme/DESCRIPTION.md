This module extends software licenses with a structured feature system based on
property-value pairs.

- **Feature properties**: define reusable property keys (e.g. "Max Users",
  "Expiry Mode") each with an optional list of allowed values.
- **Feature values**: attach predefined or custom values to each property.
- **License features**: link a set of property-value pairs to a license to
  describe exactly what is enabled or limited.
- **Template sync**: features can be pre-populated automatically from the
  application's license template via a dedicated action.
- **Export**: feature data is included in the license export payload for use by
  external systems.

## Technical details

**Models**

- `software.license.feature` - one feature line per license; references a
  `software.license.feature.property` and either a predefined
  `software.license.feature.value` (when the property is not customizable) or a
  free-text `value` field (when `property_id.customizable` is `True`). A
  `UserError` is raised on creation if the required value is missing.
- `software.license.feature.property` - master definition of a feature key.
  When `customizable=True`, value selection is replaced by a free-text input.
- `software.license.feature.value` - predefined choice for a non-customizable
  property. The display name is enriched with the parent property name for
  users in the debug/technical group.

**`software.license` extension**

- Adds `feature_ids` (One2many) to the license form.
- `action_sync_features_with_template()` deletes existing features and recreates
  them from the application's template feature set.
- `get_features_dict()` returns a `{property_name: [values]}` mapping.
- Overrides `_prepare_export_vals()` to include the features dictionary under
  the `"features"` key.
