{
    "name": "Product Reference Analytic",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "product_reference",
        "product_analytic",
        "account_analytic_parent",
    ],
    "data": [
        "data/account_analytic_account.xml",
        "views/ref_category.xml",
        "views/res_config_settings.xml",
    ],
    "post_init_hook": "post_init",
    "installable": True,
}
