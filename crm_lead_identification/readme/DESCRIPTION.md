This module improves CRM lead identification during autocomplete and search.

- It builds a richer lead label by combining the lead number, lead title, and
	related partner information when available.
- It keeps lead search robust even when users search with the full decorated
	label shown in autocomplete.
- It can prepend a stage symbol in the displayed label, while still allowing
	users to search with clean input.

## Technical details

**Context-aware lead label formatting**

The module extends `crm.lead` and adapts display-name computation when
`name_search` is enabled in context. It assembles a custom label using the lead
number and name, then appends partner and location identification details.

**Safe search input normalization**

The `name_search` and `_search_display_name` flows normalize incoming search
strings to remove module-specific separators and optional stage symbols. This
ensures compatibility with direct searches and avoids false negatives when the
decorated label is pasted back into search.

**Search index enrichment**

The module extends name computation so zip/location information is added to
`search_name`, improving hit quality for location-based searches.
