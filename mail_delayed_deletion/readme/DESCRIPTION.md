Instead of deleting sent emails immediately, this module holds them for a
configurable number of days and removes them on a scheduled basis.

- **Delayed deletion**: when a `mail.mail` record is sent with `auto_delete`
  enabled, the immediate deletion is replaced by a scheduled one. A
  `delayed_deletion` date is set on the record and `auto_delete` is turned off
  so the mail survives until the scheduler runs.
- **Configurable retention period**: the number of days to keep sent emails is
  controlled by the system parameter `mail_delayed_deletion.days` (default: 7).
- **Immediate deletion bypass**: callers that need to delete a mail right away
  can set the context key `mail_immediate_deletion=True` to skip the delay and
  let the standard `auto_delete` mechanism apply.
- **Audit logging**: every creation and deletion of `mail.mail` and
  `mail.message` records is traced to the `mail_delayed_deletion` log channel
  for debugging purposes.

## Technical details

**Delayed deletion logic**

`MailMail._postprocess_sent_message` is overridden. When a mail is sent
successfully (or fails only because of a bad recipient), and the
`mail_immediate_deletion` context key is absent, `_delay_auto_delete` is
called. That method searches for `auto_delete=True` records in the current
recordset, sets `auto_delete=False`, and writes a `delayed_deletion` date
computed as `today + delayed_deletion_days`.

**Scheduled cleanup**

`MailMail.action_delayed_deletion` is called by an hourly `ir.cron` job. It
searches for records whose `delayed_deletion` date is in the past and unlinks
them.

**Configuration parameter**

The retention period is read from the `ir.config_parameter` key
`mail_delayed_deletion.days`. A default value of `7` is provided in the module
data.
