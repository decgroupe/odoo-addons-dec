{
    "name": "CRM Lead to Helpdesk Ticket",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
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
