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
        'web_tree_dynamic_colored_field',
    ],
    'data': [
        'views/assets.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
    ],
    'installable': True
}
