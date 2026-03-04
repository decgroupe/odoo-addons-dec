{
    "name": "Purchase Split",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "purchase",
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order.xml",
        "wizard/purchase_order_split.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
