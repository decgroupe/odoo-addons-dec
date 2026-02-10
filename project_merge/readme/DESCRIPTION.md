This module allows merging project records and task records into a single
destination record.

- **Merge Projects**: consolidate multiple projects into one, preserving tasks,
  followers, and messages from all source projects.
- **Merge Tasks**: consolidate multiple tasks into one, moving messages,
  assignees, and attachments to the destination task.

After each merge, an email notification is sent to the project manager (for
project merges) or to the task assignees (for task merges).

**Technical notes**:

- Relies on `base_merge` for the core merge logic (foreign-key rewriting,
  field value propagation, XML-ID deduplication).
- Email notifications use QWeb templates provided by `mail_qweb`.
- The project type field (`project_type`) is exposed in the notification
  email template.
