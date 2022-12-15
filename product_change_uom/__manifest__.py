{
    'name': 'Product Change UoM',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Allow product UoM change if all stock moves are "
        "done or cancelled",
    'depends': ['product', 'stock'],
    'data': [
        'security/res_groups.xml',
    ],
    'installable': True
}
