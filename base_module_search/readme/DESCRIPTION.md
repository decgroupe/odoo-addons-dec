This module improves the Apps view to make it easier to inspect installed
and available modules directly from the interface.

- The "Learn More" button in the kanban card (which redirected to an
  external website) is hidden and replaced by the "Module Info" button,
  which opens the module form page inside Odoo.
- The list view of modules gains a small icon column so each module is
  visually identifiable at a glance.
- The default action opens the list view before the kanban view.

## Technical details

**Kanban view**

The `base.module_view_kanban` view is inherited via XPath to set
`invisible=True` on the "Learn More" anchor and `invisible=False` on the
"Module Info" anchor, reversing the default Odoo 18.0 behaviour.

**List view**

The `base.module_tree` view is inherited via XPath to insert an
`icon_image` field (rendered as an image widget) before the `shortdesc`
column.

**Action**

The `base.open_module_tree` window action is overridden to put `list`
first in `view_mode`, so the list view is displayed by default instead of
the kanban.

