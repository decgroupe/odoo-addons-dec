{
    "name": "Manufacturing Traceability",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "product",
        "mrp",
        "sale_stock",
        "purchase_stock",
        "stock_traceability",
        "stock_orderpoint_traceability",
        "stock_mrp_traceability",
        "web_base_view",
    ],
    "data": [
        "views/assets.xml",
        "views/stock_move.xml",
        "views/mrp_production.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}
