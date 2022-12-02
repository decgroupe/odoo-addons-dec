{
    'name': 'Tagging (base)',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':" Tagging support for every models",
    'depends': [
        'base',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/tagging.xml',
        ],
    'installable': True
}
