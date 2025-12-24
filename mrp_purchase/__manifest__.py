{
    "name": "Manufacturing Purchase",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "stock",
        "purchase_subcontracted_service",
    ],
    "data": [
        "data/mail_activity_template.xml",
        "views/mrp_production.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
