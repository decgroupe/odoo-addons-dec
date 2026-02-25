This module improves helpdesk ticket identification in search results and display labels.

- Shows a complete ticket label with its number and title for faster recognition.
- Enriches search display with team and customer identification details.
- Keeps search reliable by cleaning formatted labels before querying.

## Technical details

**Complete ticket name**

The module extends `helpdesk.ticket` with a stored computed field `complete_name`
(`_compute_names`) formatted as `[number] name`, and includes this field in
`_rec_names_search`.

**Display name enrichment during search**

`_compute_display_name` uses `complete_name` as the default label. When the
`name_search` context key is set, it builds an enriched label via
`_get_name_identifications`, adding team and partner identification details with
the `->` separator and an optional leading stage symbol.

**Search input normalization**

`name_search` and `_search_display_name` call `_clean_name_identification` to
strip separators and optional symbols from user input before delegating to the
standard search logic, avoiding false negatives when formatted labels are
searched.
