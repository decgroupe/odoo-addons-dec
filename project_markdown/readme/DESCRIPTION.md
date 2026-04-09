This module adds Markdown editing support to project tasks, allowing users to
write task descriptions using Markdown syntax alongside the standard HTML
editor.

- Adds a **Markdown Description** field on tasks rendered with a Markdown
  widget.
- Adds toggle checkboxes in the task form to independently show or hide the
  HTML description and the Markdown description.

## Technical details

**Markdown description field**

Adds a `description_markdown` (`Text`) field and two `Boolean` visibility
flags (`description_html_visible`, `description_markdown_visible`) to
`project.task`.

**View changes**

Extends `project.view_task_form2` via XPath to insert the Markdown field
after the HTML description field and to conditionally hide each field based
on the corresponding visibility flag. Two checkboxes are added in the
`extra_info` tab so users can control which description format is displayed.
