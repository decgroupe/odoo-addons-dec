Gives administrators full visibility over user-defined dashboards and improves
their searchability by indexing the creation date.

- **Admin access**: the system administrator can view and manage the custom
  dashboard layouts of all users, not just their own.
- **Indexed creation date**: the `create_date` field on custom dashboard views
  is indexed for faster queries and is exposed in the form and list views.

## Technical details

**`ir.ui.view.custom.create_date` (indexed field)**

Overrides the base `ir.ui.view.custom` model to declare `create_date` with
`index=True`. This speeds up queries that filter or order by creation date
(e.g. purging old dashboard snapshots).

**Security rules**

Two security rules are adjusted:

- `base.ir_ui_view_custom_personal`: the built-in personal rule is scoped to
  `base.group_user` so that it no longer restricts administrator visibility.
- `ir_ui_view_custom_admin`: a new rule grants `base.group_system` users
  unrestricted read-write access to all `ir.ui.view.custom` records, allowing
  admins to inspect and clean up dashboard customizations for any user.

