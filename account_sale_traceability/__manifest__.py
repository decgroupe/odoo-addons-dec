{
    "name": "Account Traceability",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "account",
        "account_usability",  # OCA module previously named "account_menu"
        "sale",
        "sales_team",
        "purchase",
    ],
    "data": [
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
