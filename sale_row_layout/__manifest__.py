{
    "name": "Sale Row Layout",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Sales",
    "depends": [
        "product",
        "sale_margin",
        "sale_stock",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_row_layout/static/src/scss/style.scss",
        ],
    },
    "installable": True,
}
