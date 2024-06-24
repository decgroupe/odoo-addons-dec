{
    "name": "CRM Lead to Helpdesk Ticket",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "crm_lead_new_email",
        "helpdesk_mgmt",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/crm_lead_to_helpdesk_ticket.xml",
        "views/crm_lead.xml",
    ],
    "installable": True,
}
