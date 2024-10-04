{
    "name": "Manufacturing (BoM supplier)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        # "mrp_prepare",
        "onchange_helper",
        "product_legacy_routes",  # needed for `supply_method` depends
        "product_seller", # needed for `main_seller_id` (delay computation)
    ],
    "data": [
        "views/mrp_bom.xml",
    ],
    "installable": True,
}
