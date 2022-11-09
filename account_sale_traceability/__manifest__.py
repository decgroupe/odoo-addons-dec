{
    'name': 'Account Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Accounting traceability",
    'depends': [
        'account',
        'sale',
        'purchase',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/sale_order.xml',
    ],
    'installable': True
}
