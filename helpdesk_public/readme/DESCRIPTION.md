This module lets external users create helpdesk tickets through a public JSON API endpoint, without needing an Odoo user account.

- Creates tickets from public payload data (name, email, subject, description).
- Accepts optional project, team, category, and channel names and maps them to existing records.
- Automatically links the ticket to an existing contact when the email already exists.
- Automatically assigns the ticket to the project manager when a project is provided.
- Forces new-ticket notifications for public ticket creation requests.

## Technical details

**Public API controller**

The controller in `controllers/main.py` exposes `POST /api/helpdesk/v1/Ticket/New` with `auth="public"` and `type="json"`.
It resolves optional relational values by searching records by name in `project.project`, `helpdesk.ticket.team`, `helpdesk.ticket.category`, and `helpdesk.ticket.channel`, then creates `helpdesk.ticket` with `sudo()` and context `public_ticket=True`.

**Ticket enrichment on create**

The `helpdesk.ticket` model override in `models/helpdesk_ticket.py` enriches incoming create values before `super().create(vals_list)`:

- `_retrieve_partner_from_email` sets `partner_id` from `partner_email` when possible.
- `_retrieve_user_from_project` sets `user_id` from the selected project's responsible user.

**Notification behavior**

`_should_notify_new_ticket` is overridden to honor the standard behavior first, then fallback to the `public_ticket` context flag so notifications are sent for tickets created through the public endpoint.
