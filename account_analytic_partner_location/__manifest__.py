{
    'name': 'Account Analytic Partner Location',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add partner location to analytic lines''',
    'depends': [
        'account',
        'base_location',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
