{
    'name': 'Tagging',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Tagging support for every models''',
    'depends': [
        'base',
        'dec',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/tagging.xml',
            'views/menu.xml',
        ],
    'installable': True
}
