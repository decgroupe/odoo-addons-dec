This module adds scheduling capabilities to activities.

- You can define a start date and an end date on activities in popup, list, and
	kanban views.
- Plannable activity types expose the planning fields so users can plan work
	windows instead of only a deadline.
- Activity dates are synchronized with related business documents and linked
	calendar events.

## Technical details

**Activity model extensions**

- `mail.activity` is extended with `date_start`, `date_stop`, and
	`activity_plannable` fields.
- The `write` override synchronizes scheduling values to related records that
	implement `_get_schedule_date_fields`.
- When an activity is linked to a `calendar.event`, activity date changes are
	propagated to event `start` and `stop`.

**Calendar synchronization**

- `calendar.event` is extended to write back `start` and `stop` into related
	activities.
- For all-day events, values are normalized to UTC boundaries before writing to
	activity fields.

**Schedulable mixin**

- `mail.activity.schedule.mixin` provides `scheduling_activity_id` and
	`schedulable` behavior.
- The `create` override uses multi-record API and creates/updates a dedicated
	scheduling activity when records are schedulable.
- `write` keeps scheduling activities synchronized and closes them when records
	are no longer schedulable.

**View integration**

- The module injects planning fields in inherited mail activity popup/list/kanban
	views and adds a search group-by filter on document name.
- `mail.activity.type` form is extended with a `plannable` toggle used by
	activity planning behavior.
