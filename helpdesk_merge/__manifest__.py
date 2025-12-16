{
    "name": "Merge Helpdesk Tickets",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "helpdesk_mgmt",
        "base_merge",  # was deltatech_merge but no more supported
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/merge_helpdesk_ticket.xml",
    ],
    "installable": True,
}
