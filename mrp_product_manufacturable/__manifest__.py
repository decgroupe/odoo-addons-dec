{
    'name': 'Manufacturing Product Manufacturable',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        'Use a new computed field to know if a product is manufacturable '
        'instead of analyzing its BoMs every time',
    'depends': [
        'product',
        'mrp',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
