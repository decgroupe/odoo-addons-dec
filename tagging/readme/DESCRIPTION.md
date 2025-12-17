This module provides a reusable tag catalog that can be used by other modules
to classify records with consistent tag names.

- Stores tags with a short code-like name, a label text, optional notes, and color.
- Automatically normalizes tag names to a clean slug format.
- Supports tag relationships to model links between related tags.
- Includes list, form, and search views to manage tags from the UI.

## Technical details

**Tag model**

The module defines the `tagging.tags` model with unique `name`, optional
`description` and `notes`, `active` archive flag, and a self-referential
many2many field `related_tags_ids`.

**Name normalization**

Name formatting is handled by `_format_name` in `models/tagging.py`. The method
unaccents characters, lowercases text, trims spaces, replaces spaces with `-`,
collapses repeated separators, and removes unsupported characters.

**Data consistency hooks**

The normalization is applied in `@api.onchange("name")`,
`@api.onchange("description")`, `create`, and `write`, ensuring values are
stored with the same formatting whether entered interactively or created by code.

**UI integration**

The module provides dedicated search, list, and form views for `tagging.tags`,
an action with `list,form` view mode, and a menu entry under the base menu tree.
