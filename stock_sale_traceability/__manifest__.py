{
    'name': 'Stock Sale Traceability',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
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
