This module improves partner identification in search results and selection widgets.

- Adds a visual type marker in partner names to quickly distinguish companies from contacts.
- Appends contextual details such as ZIP/city and email to make similar names easier to disambiguate.
- Keeps search behavior compatible when users paste back decorated names from the UI.

## Technical details

**Display-name enrichment during partner lookup**

The module extends `res.partner` and customizes `_compute_display_name`. When the
`name_search` context flag is active, it decorates the computed `display_name`
with a contact-type symbol, a separator, optional location (`zip` + `city`),
and optional email.

**Identification cleanup before search**

To avoid polluted queries, `name_search` and `_search_display_name` sanitize the
input using `_clean_name_identification`. This removes generated markers and the
separator before delegating to the standard search logic.

**Context-aware optional parts**

Extra parts are added by `_get_name_identifications`, with optional suppression
via context flags (`idf_no_location`, `idf_no_email`) for integrations that need
leaner labels.
