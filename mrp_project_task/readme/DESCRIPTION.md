This module links Manufacturing Orders with Project Tasks to make service
production easier to plan and follow.

- Automatically creates project tasks from service-type BoM lines tracked in a
	project.
- Adds direct links between each task and its originating Manufacturing Order.
- Shows task count and task list on the Manufacturing Order form.
- Displays task progress on Manufacturing Order kanban cards.
- Schedules a warning activity on open tasks when a related Manufacturing Order
	is cancelled.

## Technical details

**Task creation from BoM service lines**

`mrp.production._action_launch_procurement_rule` is extended to create a
`project.task` when the BoM line product is a service with
`service_tracking == "task_in_project"` and the production is linked to a
project. Task values are prepared by `_create_task_prepare_values`, including
hours converted from BoM quantity via `mrp.bom.line._convert_qty_company_hours`.

**Bidirectional MO/task linkage**

The module adds `project.task.production_id` and `project.task.bom_line_id`, and
`mrp.production.task_ids`. It also computes `mrp.production.task_count` and
`mrp.production.task_progress` from related open tasks.

**User interface additions**

Inherited views add a Tasks smart button and Tasks tab on Manufacturing Orders,
display `production_id` on task form/kanban views, and inject task progress in
the staged MO kanban template.

**Cancellation follow-up activity**

On `mrp.production.action_cancel`, open linked tasks receive an activity using
the `mrp_project_task.exception_task_on_mrp_cancellation` template to notify
users about required manual actions.
