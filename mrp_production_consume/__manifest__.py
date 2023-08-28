{
    "name": "Manufacturing consume line",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
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
