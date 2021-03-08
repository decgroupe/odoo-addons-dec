{
    'name': 'Product Service No Routes',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Since we consider that routes on product are only for physical "
        "items then we remove existing routes when setting a product as a "
        "service",
    'depends': [
        'product',
        'stock',
    ],
    'data': [],
    'installable': True
}
