{
    "name": "Manufacturing Swap Production",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp_timesheet",
        "sale_mrp_production_request_link",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "wizard/mrp_swap_production.xml",
        "wizard/mrp_swap_production_line.xml",
    ],
    "installable": True,
}
