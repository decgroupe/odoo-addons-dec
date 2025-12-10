{
    "name": "Sale Partner Location",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Sales",
    "depends": [
        "sale",
        "base_location",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_partner_location/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
