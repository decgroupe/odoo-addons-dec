When a member replies to a mailing-list email, their mail client typically
appends the full original message below the cursor. This module removes that
quoted content automatically so only the reply itself is stored in the group.

- Incoming replies to a mail group are stripped of everything below the
  `##- Please type your reply above this line -##` marker before being
  saved as a `mail.group.message`.
- Forwarded messages are detected and left untouched: if the body
  contains a forwarded-message header, no content is removed.

## Technical details

`MailGroup.message_post` is overridden to call
`mail.thread._remove_everything_except_above_this_line` on the message
body before delegating to `super()`. This reuses the same HTML-aware
stripping logic as `mail_above_line` (which handles `mail.thread`
subclasses), ensuring consistent behaviour across both regular threads
and mailing-list groups.

