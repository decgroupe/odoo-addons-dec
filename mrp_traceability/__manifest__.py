{
    "name": "Manufacturing Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "product",
        "mrp",
        "sale_stock",
        "purchase_stock",
        "stock_traceability",
        "stock_traceability_orderpoint",
        "web_base_view",
    ],
    "data": [
        "views/stock_move.xml",
        "views/mrp_production.xml",
        "views/stock_picking.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_traceability/static/src/scss/style.scss",
        ],
    },
    "installable": True,
    # "post_init_hook": "post_init_hook",
    # "force_post_init_hook": True,
}
