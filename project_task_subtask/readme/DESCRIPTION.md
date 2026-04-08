Use checklist to be ensure that all your tasks are performed and to make
easy control over them.

Each checklist item can be assigned to a specific user and has a state:
**To-Do**, **Done**, **Waiting**, or **Cancelled**. Progress is displayed
in Kanban view as a progress bar per assignee.

## Technical details

- Adds a new model `project.task.subtask` with state management and per-user
  progress tracking.
- Extends `project.task` with one2many subtask relationships and computed
  Kanban progress fields.
- Sends chatter messages on state, name, or assignee changes.
