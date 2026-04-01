This module limits Google Calendar integration to explicitly approved Odoo
databases.

- It prevents staging, testing, or cloned databases from synchronizing events
  with the same Google accounts as production.
- It blocks both scheduled and manual Google Calendar synchronization unless
  the current database is listed in `db_googlesync_allowedlist`.
- It keeps attendee invitation e-mails working with standard calendar behavior
  when Google sync is disabled for the database.
- It adds a duplicate counter on calendar events so users can quickly spot
  repeated events with the same title and dates.

## Technical details

**Database allowlist**

`google.calendar.sync._get_db_allowedlist()` reads the
`db_googlesync_allowedlist` configuration key, converts it into a database list,
and caches the result with `@ormcache`.

**Sync interception**

`google.calendar.sync` overrides `_sync_odoo2google`, `_sync_google2odoo`, and
`_google_insert`, while `res.users` overrides `_sync_google_calendar` and
`_sync_all_google_calendar`. Each method checks `self.env.cr.dbname` before
delegating to the Google Calendar flow. `calendar.event.action_sync2google`
also reuses the same guarded sync path for manual pushes.

**Invitation fallback**

`calendar.attendee._send_mail_to_attendees()` bypasses the
`google_calendar` override when the database is not allowed and calls the base
calendar implementation directly so attendee notifications still use the normal
mail flow.

**Duplicate counter**

`calendar.event` adds the stored computed field `duplicate_count` and exposes it
through `_get_public_fields()`. The recomputation groups records by event name,
all-day flag, and matching start or date ranges, then writes the duplicate
count back on the related events.

