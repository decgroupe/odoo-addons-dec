{
    "name": "Product Reference Analytic",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "product_reference",
        "product_analytic",
    ],
    "data": [
        "data/account_analytic_account.xml",
        "views/ref_category.xml",
    ],
    "post_init_hook": "post_init",
    "installable": True,
}
