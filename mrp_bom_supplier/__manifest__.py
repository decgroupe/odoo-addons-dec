{
    "name": "Manufacturing (BoM supplier)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "onchange_helper",
        "product_legacy_routes",  # needed for `supply_method` depends
        "product_seller",  # needed for `main_seller_id` (delay computation)
    ],
    "data": [
        "views/mrp_bom.xml",
    ],
    "installable": True,
}
