{
    'name': 'Orderpoint ignore make_to_order',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Do not execute orderpoint for product configured as "
        "make_to_stock",
    'depends': [
        'stock',
        'product_legacy_routes',
    ],
    'data': [],
    'installable': True
}
