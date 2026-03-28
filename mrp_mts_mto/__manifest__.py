{
    # To replace with `stock_mts_mto_mrp_rule` ?
    "name": "Manufacturing MTS+MTO Rule Support",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mrp",
        "stock_mts_mto_rule",  # stock-logistics-warehouse OCA module
        # "purchase_stock",  # buy route is mandatory
    ],
    "data": [],
    "installable": True,
}
