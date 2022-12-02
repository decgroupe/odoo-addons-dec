{
    'name': 'Account Sale Link',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Show related sale orders on invoice form",
    'depends': [
        'account',
        'sale',
        'sale_action_view',
    ],
    'data': ['views/account_invoice.xml', ],
    'installable': True
}
