{
    "name": "Stock Traceability (mrp_production_request)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock_traceability_mrp",
        "mrp_production_request",
        "mrp_production_request_action_view",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "installable": True,
}
