{
    "name": "Sale Row Layout",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "category": "Sales",
    "depends": [
        "product",
        "sale_margin",
        "sale_stock",
    ],
    "data": [
        "views/assets.xml",
        # FIXME: [MIG] 14.0: Disabled because issue with View name: sale.order.line.tree.sale.stock.qty
        "views/sale_order.xml",
    ],
    "installable": True,
}
