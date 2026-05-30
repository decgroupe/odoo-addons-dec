This module adds automatic scheduling activities on manufacturing orders.

- Scheduling dates are taken from planned start and finish dates.
- A scheduling activity is synchronized while the order is active.
- Completed and cancelled manufacturing orders are excluded from scheduling.

## Technical details

**Manufacturing integration**

The module extends `mrp.production` with `mail.activity.schedule.mixin` in
`models/mrp_production.py`.

**Schedule field mapping**

`_get_schedule_date_fields()` maps scheduling values to
`date_planned_start` and `date_planned_finished`, with deadline aligned to the
planned finish date.

**Schedulable conditions**

`_is_schedulable()` keeps the inherited scheduling behavior and additionally
rejects productions in `done` and `cancel` states.
