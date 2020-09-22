{
    'name': 'Purchase product Pack',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Purchase product packs''',
    'depends': [
        'purchase',
        'purchase_stock',
        'product_pack',
        'stock_auto_validate',
    ],
    'data':
        [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        ],
    'installable': True
}
