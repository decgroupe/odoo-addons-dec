Replaces plain text fields with a full-featured Markdown editor powered by
[Draftly](https://github.com/NeuroNexul/draftly) and CodeMirror.

- **Live mode** (default): WYSIWYG editing with real-time Markdown rendering.
- **Code mode**: raw Markdown source with syntax highlighting and line numbers.
- **View mode**: read-only rendered HTML preview with a "Save as PDF" button.
- **Output mode**: inspect the generated HTML and CSS source side by side.
- **Formatting toolbar**: one-click insertion of headings, bold, italic, quotes,
  code blocks, links, numbered lists, unordered lists and task lists - visible
  in Live and Code modes only.
- **Sticky toolbar**: the toolbar stays visible while scrolling through long
  documents.
- **Save as PDF**: in View mode, triggers the browser print dialog scoped to
  the preview pane only - the rest of the page is hidden.

## Technical details

**Widget registration**

The `markdown` widget is registered in the Odoo field registry under the
`"text"` supported type. It is implemented as an OWL `Component`
(`MarkdownField`) and declared in `static/src/js/web_widget_markdown.esm.js`.

**Draftly bundle**

The editor relies on a self-contained IIFE bundle
(`static/src/lib/draftly.bundle.js` / `.css`) built by `build_draftly.sh`
using esbuild. The bundle exposes a global `window.Draftly` object containing
`EditorState`, `EditorView`, `draftly`, `allPlugins`, `preview`, `generateCSS`,
and a pre-built `codeExtensions` array (line numbers + active-line highlight +
syntax highlighting) used in Code mode. The bundle is loaded lazily via
`loadJS` / `loadCSS` in `onWillStart`.

**Mode switching**

The component tracks `state.renderMode` (`live`, `view`, `code`, `output`).
Live and Code modes instantiate a CodeMirror `EditorView` inside
`this._editorView`; switching between them destroys and recreates the editor
because different Draftly options are needed (`disableViewPlugin` for Code).
View and Output modes destroy the editor and call async render helpers
(`_renderPreview`, `_renderOutput`) that use Draftly's `preview()` and
`generateCSS()` APIs.

**Formatting actions**

`_applyMarkdown(view, action)` dispatches CodeMirror transactions directly:
wrap actions (bold, italic, inline code, code block, link) insert delimiters
around the current selection; prefix actions (heading, quote, numbered/
unordered/task list) insert a prefix at the start of the current line.

**Print / Save as PDF**

`onPrint()` adds the CSS class `o_printing_markdown` to `<body>`, calls
`window.print()`, and removes the class automatically via the `afterprint`
event. The `@media print` block in the SCSS is scoped to
`body.o_printing_markdown` so that a regular Ctrl+P prints the full page.
