{
    'name': 'Account Partner Location',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add partner location to invoices and accounting lines",
    'depends': [
        'account',
        'base_location',
    ],
    'data': ['views/account_invoice.xml', ],
    'installable': True
}
