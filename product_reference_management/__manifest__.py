{
    'name': 'Product Reference Management',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Root module for reference management (menu/security)",
    'depends': [
        'product',
    ],
    'data':
        [
            'security/model_security.xml',
            'security/ir.model.access.csv',
            'views/menu.xml',
        ],
    'installable': True
}
