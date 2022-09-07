{
    'name': 'Stock Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Get move final location from any move of the chain",
    'depends':
        [
            'stock',
            'stock_actions',
            'purchase',
            'purchase_action_view',
            'purchase_stock',
            'mrp',
            'mrp_action_view',
            'mail',
            'mail_action_view',
            'product_supplierinfo_picking',
            'web_tree_dynamic_colored_field',
            'web_base_view',
        ],
    'data':
        [
            'views/assets.xml',
            'views/stock_picking.xml',
            'views/stock_move.xml',
        ],
    'installable': True
}
