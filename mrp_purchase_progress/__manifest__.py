{
    "name": "Manufacturing Purchase Progress",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "mrp_stage",
        "mrp_partner",
        "mrp_supply_progress",
        "purchase_stock",
    ],
    "data": [
        "data/mrp_production_cron.xml",
        "views/mrp_production.xml",
    ],
    "installable": True,
}
