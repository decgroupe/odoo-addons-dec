{
    'name': 'Sale Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': '''Show related stock moves on sale order line form''',
    'depends': [
        'sale_traceability',
        'sale_row_layout',
        'stock_mrp_traceability',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/res_groups.xml',
            'views/sale_order.xml',
            'views/stock_move.xml',
        ],
    'installable': True
}
