This module adds automatic scheduling activities on projects and tasks.

- Projects become schedulable from their start and end dates.
- Tasks become schedulable from assigning, ending, and deadline dates.
- Scheduling activities are created and synchronized automatically for existing
	and updated records.

## Technical details

**Project integration**

The module extends `project.project` with `mail.activity.schedule.mixin` in
`models/project_project.py`. It maps schedule fields to `date_start` and `date`
and restricts scheduling to active projects through `_is_schedulable()`.

**Task integration**

The module extends `project.task` with `mail.activity.schedule.mixin` in
`models/project_task.py`. It maps schedule fields to `date_assign`, `date_end`,
and `date_deadline` so task scheduling follows Odoo 18.0 task date fields.

**Post-init synchronization**

The `post_init_hook` in `hooks.py` scans existing projects and tasks,
filters schedulable records, and calls `_ensure_scheduling_activity()` to
initialize scheduling activities after module installation.
