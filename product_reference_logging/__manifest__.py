{
    'name': 'Product Reference Logging',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Logging for REFManager user actions''',
    'depends': [
        'product_reference_management',
    ],
    'data':
        [
            'security/model_security.xml',
            'security/ir.model.access.csv',
            'views/ref_log.xml',
            'views/menu.xml',
        ],
    'installable': True
}
