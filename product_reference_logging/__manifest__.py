{
    'name': 'Product Reference Logging',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
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
