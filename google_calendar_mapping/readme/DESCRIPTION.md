This module lets Odoo users synchronize Google Calendar even when their Odoo
email address is different from their Google calendar identifier.

- Incoming events from Google are mapped from Google attendee emails to the
  matching Odoo user email.
- Outgoing events from Odoo are mapped from Odoo user emails to each user's
  configured Google calendar identifier.

## Technical details

**Incoming sync (Google to Odoo)**

The module overrides `calendar.event._odoo_attendee_commands` and, before
delegating to the base implementation, rewrites each attendee email by
searching `res.users.google_calendar_cal_id` and replacing it with the user's
Odoo email.

**Outgoing sync (Odoo to Google)**

The module overrides `calendar.event._google_values` and rewrites both
organizer and attendee emails to `res.users.google_calendar_cal_id` when
available, so Google receives identifiers expected by Google Calendar.
