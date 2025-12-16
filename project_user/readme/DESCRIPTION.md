This module improves assignment workflows on projects and tasks.

- Adds an "Assign to Me" action on projects so users can quickly become the
	responsible person.
- Adds an "Assign to Me" action on tasks so users can add themselves to the
	assignees list.
- Adds default task assignees at project level and automatically pre-fills
	those users when creating a task from that project.

## Technical details

**Project assignment**

The module extends `project.project` with `action_assign_to_me`, which writes
`user_id` with the current user. The project form view is inherited to add an
object button in the header and to display `default_task_user_ids` after
`user_id`.

**Task assignment and defaults**

The module extends `project.task` with `action_assign_to_me`, which links the
current user in `user_ids` using `Command.link`. It also overrides
`default_get` to read `default_project_id` from context and prefill `user_ids`
with `Command.set(project.default_task_user_ids.ids)` when a task is created
from a project.
