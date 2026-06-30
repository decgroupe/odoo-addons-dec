This module ensures proper context management for helpdesk tickets when creating timesheets. It allows users to select a helpdesk ticket on a timesheet entry and automatically populates the project and task information from the ticket, ensuring consistent project assignment across timesheets and helpdesk workflows.

- Automatically set the project context when selecting a ticket on a timesheet entry.
- Link timesheets directly to helpdesk tickets with automatic project and task assignment.
- Prevent context loss when creating timesheets from ticket-related activities.

## Technical details

**Helpdesk Ticket Name Management**

The `helpdesk.ticket` model is extended to ensure the ticket name is properly set from the ticket number during creation, providing correct naming conventions for ticket records.

**Ticket-Based Project Context on Timesheets**

The `account.analytic.line` model is extended with a new `ticket_id` field that allows linking timesheets to helpdesk tickets. The field includes:
- A dynamic domain that filters tickets by the currently selected project.
- An `onchange` handler that automatically sets the project and task from the selected ticket, ensuring consistent context.
- Smart project assignment logic that respects manual project selections while still allowing automatic assignment when no project is set.
