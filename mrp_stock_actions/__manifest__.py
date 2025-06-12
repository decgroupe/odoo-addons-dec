{
    "name": "Manufacturing Stock Actions",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "sale_stock",
        "stock_actions",
    ],
    "data": [
        "views/mrp_production.xml",
    ],
    "installable": False,
    "pre_init_hook": "rename_module",
}
