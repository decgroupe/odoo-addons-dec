{
    "name": "Account Recreate Analytic Lines",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "account",
        "product_analytic",
        "product_category_analytic",
        "account_invoice_update_wizard",  # akretion/odoo-usability
    ],
    "data": [
        "views/account_invoice.xml",
        "wizard/account_invoice_update.xml",
    ],
    "installable": True,
}
