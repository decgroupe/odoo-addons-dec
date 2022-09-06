{
    'name': 'Procurement Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add procurement view to track moves",
    'depends':
        [
            'sale',
            'sale_action_view',
            'purchase',
            'purchase_action_view',
            'stock',
            'stock_action_view',
            'sale_stock',
            'purchase_stock',
            'purchase_line_procurement_group',
            'mrp',
            'mrp_action_view',
        ],
    'data':
        [
            'views/procurement.xml',
            'views/mrp_production.xml',
            'views/stock_move.xml',
            'views/stock_picking.xml',
            'views/sale_order.xml',
            'views/purchase_order.xml',
            'views/menu.xml',
        ],
    'installable': True
}
