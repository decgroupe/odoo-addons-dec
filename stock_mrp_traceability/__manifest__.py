{
    "name": "Stock Manufacturing Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "mrp_production_request",
        "mrp_production_request_action_view",
        "mrp_traceability",
        "stock_traceability",
        "stock_orderpoint_traceability",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "installable": True,
}
