When a user replies to an Odoo notification email, their mail client typically
appends the full original message below the cursor. This module removes that
quoted content automatically so only the reply itself is stored on the record.

- Incoming replies are stripped of everything below the
  `##- Please type your reply above this line -##` marker before being
  saved as a `mail.message` on the record.
- Forwarded messages are detected and left untouched: if the body
  contains a forwarded-message header, no content is removed.
- Empty bodies are returned unchanged without raising an error.

## Technical details

`mail.thread.message_post` is overridden to call
`_remove_everything_except_above_this_line` on the message body before
delegating to `super()`. The method parses the HTML body with `lxml`,
walks every node, and replaces the first blockquote element that contains
the marker with a `<i>##- Content Removed -##</i>` placeholder. The
detection of forwarded messages uses a regex pattern matching
`--- Forwarded Message ---` or `--- Forwarded message ---`: when that
text is encountered before the marker, the walk stops and the body is
left untouched.

