{
    "name": "Account Recreate Analytic Lines",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "account",
        "product_analytic",
        "product_category_analytic",
        "account_invoice_update_wizard",
    ],
    "data": [
        "views/account_invoice.xml",
        "wizard/account_invoice_update.xml",
    ],
    # 'force_post_init_hook': True,
    "post_init_hook": "post_init",
    "installable": True,
}
