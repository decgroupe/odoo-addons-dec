{
    "name": "CRM Lead Number",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "crm",
        "base_sequence_first_number",
    ],
    "data": [
        "data/ir_sequence.xml",
        "data/ir_actions_server.xml",
        "views/crm_lead.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
