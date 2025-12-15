This module assigns a unique number to each CRM opportunity and keeps this
number visible in labels and searches.

- A sequence-based Opportunity Number is generated automatically when a lead
	becomes an opportunity.
- Opportunity labels are displayed with the number prefix, for example
	[OPP00042] Opportunity Name.
- Searching opportunities is improved by indexing number, name, email, and
	customer in a dedicated searchable value.

## Technical details

**Sequence generation on create and write**

The module extends crm.lead with a readonly number field and initializes it
through _init_number(), called from both create() and write(). The sequence is
provided by ir.sequence using code crm.lead.sequence, and the company context is
applied when company_id is present in incoming values.

**Computed naming and lookup behavior**

The module computes complete_name and search_name in _compute_names().
complete_name is built as [number] + name, and search_name is enriched with
email and partner display name when available. _compute_display_name() is
overridden to expose complete_name as display_name, and _rec_names_search is
set to search_name to improve native name_search coverage.
