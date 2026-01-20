Automatically create or reuse the project linked to a manufacturing order.

- When a manufacturing order is created, the module creates a project automatically if needed and links the order to it.
- If a matching project already exists for the same name and customer, it is reused instead of creating a duplicate.
- The automatic behavior can be disabled with the `mrp_project_auto_disable` context key.
- The manual project creation action can also create or relink the project for an existing manufacturing order.

## Technical details

The module extends `mrp.production.create()` to inspect each incoming value set before the record is created. When project auto-creation is enabled, it calls `_create_or_retrieve_project()` to search for an existing `project.project` by name and partner, or to create one from `_get_project_data()` when needed.

If a project is found or created, `_attach_to_project()` injects the resulting `project_id` into the manufacturing order values so the link is stored at creation time. The same lookup and attachment flow is reused by `action_create_project()` for existing manufacturing orders.

When the sale order is available in the creation values, the project data uses the sale order name and customer instead of the manufacturing order name, so the linked project stays aligned with the commercial document.
