This module helps monitor migration progress for Odoo addons.

- Track migration status directly on module records.
- Provide a simple operational view to identify what is pending, in progress, or done.

## Technical details

**Module tracking extension**

The module extends the module-tracking data model to store migration-related
status fields used by migration workflows.

**Status visibility in the interface**

The module updates related views so migration status values are visible and
usable from standard module management screens.
