{
    'name': 'Manufacturing Product Pack',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add support for product packs''',
    'depends': [
        'mrp',
        'stock_product_pack',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
