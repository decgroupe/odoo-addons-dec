{
    "name": "Manufacturing Swap Production",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp_timesheet",
        "sale_mrp_production_request_link",
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/mrp_swap_production.xml",
        "wizard/mrp_swap_production_line.xml",
    ],
    "installable": True,
}
