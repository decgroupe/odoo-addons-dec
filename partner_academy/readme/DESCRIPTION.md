This module helps classify contacts by French education academies and keeps that classification easy to maintain.

- Adds an Academy catalog where each academy can store a rectorate contact, logo, country/state, covered departments, and one or more email domains.
- Adds an Academy field on contacts so users can assign the academy manually when needed.
- Automatically suggests the academy when a contact email matches one of the configured academy email domain suffixes.

## Technical details

**Academy master data**

The module introduces the `res.partner.academy` model with fields for `partner_id`, `email_domain`, geographical links (`country_id`, `state_id`, `department_ids`), and a related editable `logo` from the rectorate partner image.

**Partner integration**

The module extends `res.partner` with `academy_id`. In `_onchange_email`, it calls `_set_academy_from_email`, which extracts the domain and delegates to `_set_academy_from_domain`.

**Domain-based auto-detection**

`_set_academy_from_domain` searches academies having an `email_domain`, splits configured values on spaces, and assigns `academy_id` when the partner email domain ends with one of those suffixes.

**User interface**

The partner form inherited from `base.view_partner_form` inserts `academy_id` after categories. The module also defines academy list/form views and a configuration menu entry under Contacts.
