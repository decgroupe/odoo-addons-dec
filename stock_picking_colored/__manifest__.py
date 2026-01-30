{
    "name": "Stock Picking Colored",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "web_tree_dynamic_colored_field",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_picking_colored/static/src/xml/list.xml",
            # "stock_picking_colored/static/src/js/list_renderer.esm.js",
        ],
    },
    "installable": True,
}
