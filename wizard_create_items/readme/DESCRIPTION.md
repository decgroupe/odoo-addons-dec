This module provides a reusable base wizard to create records from pasted content.

- Accepts item lists from HTML tables, HTML lists, dashed lines, or plain text lines.
- Supports identifier and name extraction with automatic separator detection.
- Lets users review generated lines before a child module creates business records.

## Technical details

**Wizard models**

The transient model `create.items.wizard` stores the source content, parses it on
onchange, and populates `line_ids` with `Command.create(...)`. The method
`action_create_items` validates input and is designed to be overridden by child
modules to implement actual record creation logic.

**Parsing pipeline**

The helper `_extract_items_from_html` in `utils.py` applies a fallback pipeline:
table rows first, then `<ul>/<ol>` list items, then plain text parsing. Plain text
entries can be split into `(identifier, name)` pairs using detected or provided
separators, and duplicates are removed while preserving input order.
