{
    'name': 'Stock Picking Line Autofill',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Auto encode picking line''',
    'depends': [
        'stock',
        'stock_move_line_auto_fill',
    ],
    'data':
        [
            'views/stock_picking.xml',
        ],
    'installable': True
}
