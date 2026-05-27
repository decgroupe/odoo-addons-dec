This module adds a project dashboard for project types.

- It lets you mark project types as dashboard-enabled and configure how their projects are grouped.
- It adds a kanban dashboard with project counts, year-based shortcuts, and quick access to projects and tasks.
- It adds dashboard-specific project fields and filters so users can find the right projects faster.

## Technical details

**Project type dashboard data**

The module extends `project.type` with dashboard settings and computed counters.
`_compute_todo_projects` aggregates projects by type, assigned user, and year.
`_compute_kanban_dashboard` serializes the dashboard payload used by the kanban view.
The action methods open filtered project or task views from the dashboard tiles.

**Project views and filters**

The module extends `project.project` with a stored `type_date` field and a dashboard sequence.
It updates `type_date` when the source field changes and customizes the kanban quick create view.
It also adds dashboard filters and inherited views for the project form, kanban, and project type screens.
