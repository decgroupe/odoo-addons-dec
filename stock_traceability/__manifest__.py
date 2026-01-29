{
    "name": "Stock Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "stock_actions",
        "purchase",
        "purchase_action_view",
        "purchase_stock",
        "mrp",
        "mrp_action_view",
        "mail",
        "mail_action_view",
        "product_location",
        "product_small_supply",
        "product_supplierinfo_picking",
        "stock_picking_colored",
        "web_base_view",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "assets": {
        "web.assets_tests": [],
        "web.assets_backend": [
            "stock_traceability/static/src/scss/style.scss",
        ],
    },
    "installable": True,
}
