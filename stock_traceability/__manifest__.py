{
    "name": "Stock Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock_actions",  # public access to  assign/cancel/etc. actions
        "mail_action_view",  # mail activity support for product exceptions
        "product_location",  # product rack, row, case locations
        "product_supplierinfo_picking",  # vendor product code/name
        "web_base_view",  # common styles
        # "stock_picking_colored",
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
