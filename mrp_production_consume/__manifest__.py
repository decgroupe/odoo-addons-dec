{
    "name": "Manufacturing consume line",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production.xml",
        "wizard/mrp_consume.xml",
    ],
    "installable": True,
}
