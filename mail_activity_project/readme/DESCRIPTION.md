This module links every mail activity to a project so that activities can be
filtered and grouped by project directly from the activity board or list.

- A `project_id` field is automatically computed on each `mail.activity` record
  based on the document it is attached to.
- When the project of a task or any other record changes, the related activities
  are updated automatically.

## Technical details

**Project computation (`mail.activity`)**

A stored computed field `project_id` is added to `mail.activity` and recomputed
whenever `res_model` or `res_id` changes. If the linked document is a
`project.project`, the activity is directly associated with it. Otherwise, the
code looks for a field whose name is returned by `_get_project_field_name()` on
the linked record and retrieves the project from there.

**Automatic propagation (`mail.activity.mixin`)**

`MailActivityMixin.create` and `MailActivityMixin.write` are overridden so that
when the project field on a document changes, all linked activities are updated
via `_update_activity_project()`. Models that store their project under a
different field name can override `_get_project_field_name()` to customise this
behaviour.
