{
    "name": "Purchase MRP Product Pack",
    "version": "18.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "purchase_mrp",
        "purchase_stock",
        "purchase_line_procurement_group",
        "product_pack",
        "stock_auto_validate",
        "stock_picking_line_auto_fill",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
