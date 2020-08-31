{
    'name': 'Sale Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'category': 'Sales',
    'summary': '''Show related stock moves on sale order line form''',
    'depends': [
        'sale',
        'stock_mrp_traceability',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/sale_order.xml',
            'views/stock_move.xml',
        ],
    'installable': True
}
