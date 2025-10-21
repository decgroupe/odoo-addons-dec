This module exposes a JSON REST API that allows IoT devices and external systems
to create, update, and close maintenance requests in Odoo without a user session.

- **Create or update**: a single endpoint creates a new request when none is
  open for the given equipment and identifier, or updates the existing open one.
- **Close**: a dedicated endpoint archives the active request and posts a closing
  note with an optional reason.
- **Ping**: when an update call carries no changed data, a lightweight ping note
  is posted on the request chatter instead.
- **Activity management**: upon creation, a maintenance activity is automatically
  assigned to the most relevant user (assigned technician, team leader, or
  equipment category technician).

## Technical details

**API authentication**

All endpoints are secured with an API key (`auth="api_key"`), provided by the
`auth_api_key` module. No user session is required.

**Endpoints** (JSON, POST)

- `/api/maintenance/v1/serial/<serial>/id/<identifier>/Request` - create or
  update a maintenance request identified by equipment serial number and a
  `unique_identifier` field added to `maintenance.request`.
- `/api/maintenance/v1/serial/<serial>/id/<identifier>/CloseRequest` - close
  (archive) an active request and post a closing chatter note.

**Model extension**

`maintenance.request` is extended with a `unique_identifier` (`Char`) field
used to correlate API calls with existing open requests.

**Remote methods on `maintenance.request`**

- `_remote_create`: looks up the equipment by serial number, creates the request,
  resolves the responsible user via `_get_activity_user`, schedules a maintenance
  activity, and posts a creation note.
- `_remote_update`: applies changed fields, posts an update or ping note, and
  recreates the activity if it was dismissed.
- `_remote_close`: posts a closing note, cancels the open activity, and calls
  `archive_equipment_request` (provided by `maintenance_archive`).

**Context handling**

Because API-key requests carry no user session, `get_context()` (controller
helper) merges the authenticated user's language and timezone into the
environment context before any ORM operation.
