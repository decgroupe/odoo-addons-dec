Allows users to maintain two distinct email signatures:

- **Full signature** (`signature_text`): used in new messages and standalone emails.
- **Short signature** (`signature_answer`): used automatically when replying or in
  internal messages, to reduce noise in conversation threads.

Signatures can be generated from configurable **Mako templates** (`res.users.signature.template`)
that pull employee data (name, job title, phone, email, websites, social links) and
support per-department branding (logo URL, primary colour).

## Technical details

- `mail.thread._notify_by_email_prepare_rendering_context` is overridden so that
  reply/internal notifications use `signature_answer` instead of the default
  `signature` field.
- `res.users.SELF_WRITEABLE_FIELDS` is extended so users can update their own
  signature fields from the Preferences screen without requiring administrator rights.
- The HTTP controller at `/web/signature/logo/<int:user_id>` serves per-user
  signature logo images.

