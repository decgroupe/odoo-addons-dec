This module links Manufacturing Orders and Projects so production work can be
tracked directly from the project workspace.

- Add a Project field on Manufacturing Orders to associate each MO with a
	project.
- Show linked productions on the Project form with a smart button that opens
	related Manufacturing Orders.
- Display production counters on the Project kanban card, with a configurable
	label.
- Add an "Open Productions" project filter to quickly identify projects with
	unfinished productions.

## Technical details

**MRP production extension**

The module extends `mrp.production` with a `project_id` Many2one to
`project.project`, and injects this field into production list, search, and
form views.

**Project extension**

The module extends `project.project` with:

- `production_ids` One2many inverse of `mrp.production.project_id`.
- Stored counters (`production_count`, `todo_production_count`) computed from
	linked productions and their states.
- `label_productions`, a translatable label used in project kanban statistics.

**Navigation and UI integration**

The `action_view_productions` method opens related productions from the project
smart button and kanban link:

- Opens a list action when multiple productions are linked.
- Opens the production form directly when only one production is linked.
