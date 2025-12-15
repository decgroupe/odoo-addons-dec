This module provides a reusable mixin that improves quick search in relational
dropdowns and name search fields.

- It adds a normalized search value so records can still be found when users
	type without spaces or punctuation.
- It reduces the need for custom hard-coded filter domains in search views.
- It can be inherited by any model that needs a more tolerant name search
	behavior.

## Technical details

**Typefast computed field**

The mixin defines a stored computed field named typefast_name. It computes this
value from either the model rec_name field or display_name, depending on
_typefast_options. When strip is enabled, non-word characters are removed with
a regex to build a compact searchable token.

**Search domain injection**

The mixin overrides name_search and, for ilike searches, expands the domain
with an OR on name and typefast_name. This is done through _prepare_typefast_search
and _get_typefast_domain, then combined with existing args using
odoo.osv.expression.AND.

**Customization hooks**

Inheriting models can tune _typefast_options:

- source: rec_name or display_name.
- strip: enable or disable normalization.

This allows each model to choose how typefast_name is generated while reusing
the same search extension logic.
