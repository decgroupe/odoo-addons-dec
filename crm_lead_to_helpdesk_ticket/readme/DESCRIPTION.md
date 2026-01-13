This module adds a guided conversion flow from a CRM lead to a Helpdesk ticket.

- A new Convert to Ticket button is available on active leads for sales users.
- The conversion wizard pre-fills ticket information from the lead (title, description, contact details, category, team, and assignee).
- If needed, the wizard can close the original lead after creating the ticket.
- The lead and the created ticket are linked through chatter messages for traceability.

## Technical details

**Lead action**

The module extends crm.lead with action_convert_to_helpdesk_ticket, which opens
the transient model action
crm_lead_to_helpdesk_ticket.act_crm_lead_to_helpdesk_ticket.

**Wizard defaults and validation**

The transient model crm.lead.to.helpdesk.ticket overrides default_get to
populate fields from the active lead and, when needed, fall back to the
original incoming message body/email. action_create_ticket validates that a
team or assigned user is provided and that an email is available before
creating the ticket.

**Ticket creation and notifications**

Ticket creation is delegated to helpdesk.ticket with context
force_helpdesk_notify=True (soft support for helpdesk_notify). When a user is
explicitly assigned, creation is performed with with_user(user_id), then the
record is switched back to the original user and an assignment notification is
forced via _message_auto_subscribe_notify.

**Traceability and navigation**

After creation, the wizard posts reciprocal chatter links between the lead and
the ticket, optionally marks the lead as lost when lead_close is enabled, and
returns an action that opens the created helpdesk ticket in form view.
