This module lets users generate public download links for attachments linked to a
record from the chatter.

- It adds a "Share a link" action near the attachment area in the chatter.
- It opens a wizard listing the current record's attachments and lets users
	generate a public link for each file.
- It stores the generated link on the attachment so it can be copied and reused
	later.

## Technical details

**Chatter integration**

The backend mail chatter is patched in
`static/src/js/share.esm.js` and `static/src/xml/share.xml` to add a button that
opens the `mail_attachment_share.action_attachment_sharing` window action for the
current thread model and record.

**Attachment sharing fields**

`models/ir_attachment.py` extends `ir.attachment` with `sharing_token` and the
computed `sharing_link` field. The sharing link is built from `web.base.url` and
the public sharing route. The wizard button calls
`action_generate_sharing_token_from_wizard()` to generate a UUID token and reopen
the wizard so the copied URL is immediately available.

**Wizard and public route**

`wizard/attachment_sharing.py` loads all attachments linked to the active record
into a transient model shown in a list view. Each row can generate a token and
shows the resulting URL with the `CopyClipboardURL` widget.
`controllers/main.py` exposes `/web/attachments/token/<token>` as a public HTTP
route, looks up the matching attachment with `sudo()`, and returns the file as a
download response.

