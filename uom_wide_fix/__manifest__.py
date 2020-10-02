{
    'name': 'UoM Wide Fix',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Will override existing data accross all database to match "
        "current product UoM",
    'depends': [
        'uom',
        'product',
        'sale',
        'purchase',
        'stock',
        'mrp',
    ],
    "data": ['views/product_template.xml', ],
    'installable': True
}
