Show projects' current to-do task count and a convenient filter.

- Adds a stored `To-Do Task Count` on projects that shows the number
	of currently open (not closed) tasks.
- Excludes time-tracking tasks from the count so only actionable tasks
	are considered.
- Adds a project filter "With Task To-Do" to quickly find projects
	having at least one open task, and enables this filter in the
	project's contract action context.

## Technical details

This module extends `project.project` and implements a stored computed
field `todo_task_count` implemented in `models/project.py`.

- Field: `todo_task_count` (`fields.Integer`, `store=True`)
- Compute method: `_compute_todo_task_count` — uses `_read_group` on
	`project.task` to aggregate the number of tasks per project and
	assigns the result to each project record.
- The compute method excludes tasks whose `type_id` is the
	`project_identification.time_tracking_type` (time-tracking tasks).
- A new filter is added in `views/project_project.xml` as
	`With Task To-Do` (domain: `['|', ('todo_task_count', '>', 0)]`), and
	the module updates the action context to enable this filter by
	default in the contract view.

See `models/project.py` and `views/project_project.xml` for the
implementation details.
