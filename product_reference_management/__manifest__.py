{
    'name': 'Product Reference Management',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Product reference management''',
    'depends': [
        'product',
        'dec',
    ],
    'data':
        [
            'security/model_security.xml',
            'security/ir.model.access.csv',
            'views/menu.xml',
        ],
    'installable': True
}
