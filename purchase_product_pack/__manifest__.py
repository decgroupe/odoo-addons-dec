{
    'name': 'Purchase product Pack',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Purchase product packs''',
    'depends': [
        'purchase',
        'purchase_stock',
        'product_pack',
        'stock_auto_validate',
        'stock_product_pack',
        'mrp_product_pack',
        'stock_picking_line_auto_fill',
    ],
    'data':
        [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        ],
    'installable': True
}
