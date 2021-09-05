{
    'name': 'Sale Prices',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': '''Get purchase prices using product_prices module''',
    'depends': [
        'sale_margin',
        'sale_markup',
        'product_prices',
    ],
    'data':
        [
            'views/sale_order.xml',
        ],
    'installable': True
}
