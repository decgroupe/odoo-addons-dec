{
    'name': 'Product Reference',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Manage reference management''',
    'depends': [
        'base',
    ],
    'data': [
        'views/reference_wizard.xml',
        'security/model_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
