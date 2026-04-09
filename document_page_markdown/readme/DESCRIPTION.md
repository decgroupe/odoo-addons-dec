This module adds Markdown editing support to Document Pages, allowing users
to write page content in Markdown syntax alongside the standard HTML editor.

- Adds a **Markdown Content** field on document pages rendered with a Markdown
  widget.
- Extends the history mechanism so Markdown content is stored with each
  revision, keeping a full Markdown audit trail alongside the HTML content.
- Extends the document page search filter to also search inside the Markdown
  content field.

## Technical details

**Markdown content field**

Adds a `content_markdown` (`Text`) field to both `document.page` and
`document.page.history`.

**Automatic history tracking**

Overrides `write()` on `document.page` to detect changes in
`content_markdown` and create a new history entry (via `_create_history`)
whenever the markdown content differs from the current `history_head`. This
mirrors the existing HTML content tracking logic. Only pages of type
`content` trigger history creation; category pages are skipped.

Overrides `_create_history()` to ensure `content_markdown` is always stored
in the history record, even when the caller does not supply it (e.g. when
called from the base module's `_inverse_content`).
