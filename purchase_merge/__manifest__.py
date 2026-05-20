{
    "name": "Purchase Merge",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
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
