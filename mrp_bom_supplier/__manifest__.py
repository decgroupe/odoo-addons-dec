{
    "name": "Manufacturing (BoM supplier)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mrp",
        "mrp_prepare",
        "product_legacy_routes",  # Needed for `supply_method` depends
    ],
    "data": [
        "views/mrp_bom.xml",
    ],
    "installable": True,
}
