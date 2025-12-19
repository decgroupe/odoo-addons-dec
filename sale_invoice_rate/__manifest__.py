{
    "name": "Sale Invoice Rate",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "sale",
        # account_tax_group_widget_base_amount
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_invoice_rate/static/src/xml/tax_totals.xml",
        ],
    },
    "installable": True,
}
