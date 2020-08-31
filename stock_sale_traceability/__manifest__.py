{
    'name': 'Stock Sale Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Show sale line origin''',
    'depends':
        [
            'sale_stock',
            'stock_traceability',
        ],
    'data': [
        'views/stock_move.xml',
    ],
    'installable': True
}
