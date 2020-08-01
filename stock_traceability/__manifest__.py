{
    'name': 'Stock Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Get move final location from any move of the chain''',
    'depends': [
        'stock',
        'purchase',
        'purchase_stock',
        'mrp',
        'mail',
    ],
    'data': [
        'views/assets.xml',
        'views/stock_picking.xml',
    ],
    'installable': True
}
