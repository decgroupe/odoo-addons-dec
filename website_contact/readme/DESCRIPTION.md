This module customizes the public contact flow for helpdesk tickets and CRM leads.

- It adds a website contact form for creating helpdesk tickets without a user account.
- It adds a two-step contact flow for CRM leads, including attachment handling and recaptcha checks.
- It extends helpdesk categories so public ticket routing can be configured from the backend.

## Technical details

**Public contact controllers**

The module implements a `http.Controller` with routes for ticket and lead creation.
It renders the contact form with translated labels, validates recaptcha before submit, and creates `helpdesk.ticket` or `crm.lead` records in a savepoint.
When a matching partner is found, the controller subscribes that partner and stores uploaded attachments on the created record.

**Backend configuration**

The module extends `helpdesk.ticket.category` with public routing fields used by the contact form.
It also inherits the helpdesk category form and list views to expose the new fields, and publishes the `/contact` page template used by the public website flow.
