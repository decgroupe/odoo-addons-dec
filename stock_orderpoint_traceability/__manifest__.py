{
    "name": "Stock Orderpoint Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "stock",
        "stock_action_view",
        "stock_traceability",
        # "stock_orderpoint_mrp_link",  # useless since Odoo 13.0
        "stock_orderpoint_purchase_link",
        "purchase_action_view",
    ],
    "data": [],
    "installable": True,
}
