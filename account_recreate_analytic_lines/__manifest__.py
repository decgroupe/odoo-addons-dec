{
    'name': 'Account Recreate Analytic Lines',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Recreate analytic lines from product/category accounts''',
    'depends': [
        'account',
        'product_analytic',
        'account_invoice_update_wizard',
    ],
    'data': [
        'views/account_invoice.xml',
    ],
    'installable': True
}
