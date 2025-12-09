{
    "name": "Product legacy routes",
    "version": "14.0.1.0.0",
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
    "installable": False,
    "force_post_init_hook": True,
    "post_init_hook": "post_init_hook",
}
