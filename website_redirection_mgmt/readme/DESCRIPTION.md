This module extends the website redirection (rewrite) feature with
classification and tracking fields, making it easier to manage large
numbers of redirects.

- **Grouping**: assign a redirect to a named group (e.g. campaign, project)
  to filter and report on related redirects together.
- **UTM sources**: link one or more UTM content sources to a redirect,
  recording where the traffic originates.
- **UTM target**: link a UTM content target to describe the destination
  context (e.g. image, video).
- **Look**: specify the physical representation of the link
  (clickable link, clickable image, or scannable QR code).
- **Tags**: attach colour-coded UTM tags for free-form classification
  and filtering.
- **Note**: add an HTML note to document the purpose of a redirect.

## Technical details

**New model: `website.rewrite.group`**

A simple grouping model (`_name = "website.rewrite.group"`) with a `name`
and a `note` field. Groups appear as a Many2one on redirect records and can
be used to filter or group-by in the list/search views.

**Extension of `website.rewrite`**

The following fields are added via `_inherit`:

- `group_id` (Many2one to `website.rewrite.group`)
- `content_source_ids` (Many2many to `utm.source`)
- `content_target_id` (Many2one to `utm.source`)
- `look` (Selection)
- `tag_ids` (Many2many to `utm.tag`)
- `note` (Html)

An `@api.onchange` on `url_from`/`url_to` auto-generates the record `name`
from both URLs (formatted as `/from 🡢 /to`) when the name is empty or still
contains the auto-generated arrow pattern.

