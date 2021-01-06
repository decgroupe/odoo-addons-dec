{
    'name': 'Product Reference Analytic',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Product reference analytic linking''',
    'depends': [
        'product_reference',
        'product_analytic',
        'account_analytic_parent',
    ],
    'data':
        [
            'data/account_analytic_account.xml',
            'views/ref_category.xml',
        ],
    'installable': True
}
