This module records user actions performed in the Reference Manager (REFManager)
application, providing a traceable audit log of all reference operations.

- **Audit log**: every reference operation is stored with the operator's Odoo
  username, the local Windows username, the computer name, and the client IP
  address.
- **Read-only history**: log entries can only be created or read, never
  modified or deleted, ensuring the integrity of the audit trail.

## Technical details

**ref.log model**

A new `ref.log` model is added with the following fields: `operation` (text
description of the action), `username` (Odoo user), `localusername` (local OS
username), `localcomputername` (client machine name), `ipaddress`, and
`datetime` (defaulting to the current date/time).

Records are ordered newest-first (`_order = "id desc"`).

**Security**

A dedicated `Logging User` group (`group_ref_log_user`) is introduced under
the Reference Manager category. Members of this group can read and create log
entries. The existing `Reference Manager` group automatically implies this
group so that all reference managers have logging access.
