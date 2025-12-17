{
    "name": "Product legacy routes",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "purchase_stock",
        "mrp",
        "stock_mts_mto_rule",
    ],
    "data": [
        "views/product_template.xml",
    ],
    "installable": True,
    "force_post_init_hook": True,
    "post_init_hook": "post_init_hook",
}
