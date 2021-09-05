{
    'name': 'Account Purchase Link',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Show related purchase orders on invoice form''',
    'depends': [
        'account',
        'purchase',
    ],
    'data': ['views/account_invoice.xml', ],
    'installable': True
}
