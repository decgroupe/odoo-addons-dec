{
    'name': 'Stock Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Show picking line origin",
    'depends':
        [
            'stock',
            'mrp',
            'mrp_production_request',
            'mrp_production_request_action_view',
            'stock_traceability',
            'stock_orderpoint_traceability',
        ],
    'data': [
        'views/stock_picking.xml',
        'views/stock_move.xml',
    ],
    'installable': True
}
