{
    "name": "Purchase Merge",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "purchase",
        "purchase_stock",
        "purchase_line_procurement_group",
        "onchange_helper",
    ],
    "data": [
        "views/purchase_order.xml",
        "views/template.xml",
        "wizard/purchase_order_merge.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/data.xml",
    ],
    "installable": True,
}
