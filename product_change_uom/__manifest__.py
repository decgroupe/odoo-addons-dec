{
    'name': 'Product Change UoM',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Allow product UoM change if all stock moves are "
        "done or cancelled",
    'depends': ['product', 'stock'],
    'data': [
        'security/res_groups.xml',
    ],
    'installable': True
}
