This module enriches project and task identification by adding type information
to their display names, making it easier to quickly locate records in dropdown
searches.

- Projects: the display name shown in search results includes the project type
  (e.g. `My Project → Contract`), and a stage symbol prefix is applied when the
  type name starts with a non-alphabetical character.
- Tasks: the display name shown in search results includes the parent project
  name (with its type symbol prefix when applicable), separated by the `→`
  arrow.
- Projects also expose two computed boolean fields (`is_contract`,
  `is_time_tracking`) that reflect whether the project belongs to a predefined
  contract or time-tracking type.

## Technical details

**Project display name enrichment**

`project.project` overrides `_compute_display_name` to append the project type
`complete_name` after a `→` separator when the `name_search` context key is
set. The `name_search` method strips the identification suffix before
forwarding the query to the base ORM, so existing search behaviour is
preserved. `_search_display_name` applies the same cleaning as a fallback for
direct calls.

**Task display name enrichment**

`project.task` follows the same pattern: `_compute_display_name` appends the
parent project name (with a type symbol prefix) and `_clean_name_identification`
removes both the `→` separator and the stage symbol prefix before searching.

**Computed boolean fields**

`is_contract` and `is_time_tracking` are stored computed fields on
`project.project` that compare `type_id` against the XML records
`project_identification.contract_type` and
`project_identification.time_tracking_type`. A `post_init_hook` recomputes
these fields after module installation.
