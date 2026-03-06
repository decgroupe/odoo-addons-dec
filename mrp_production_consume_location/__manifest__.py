{
    "name": "Manufacturing Product Location on Consume Line",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp_production_consume",
        "product_location",
    ],
    "data": [
        "wizard/mrp_consume.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_production_consume_location/static/src/scss/style.scss",
        ],
    },
    "installable": True,
}
