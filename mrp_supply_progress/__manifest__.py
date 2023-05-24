{
    "name": "Manufacturing Picked Rate",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "mrp_partner",
        "mrp_stage",
    ],
    "data": [
        "data/mrp_production_cron.xml",
        "data/mrp_production_stage.xml",
        "views/mrp_production.xml",
    ],
    "pre_init_hook": "rename_module",
    "installable": True,
}
