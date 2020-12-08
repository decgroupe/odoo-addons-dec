{
    'name': 'Purchase Delivery Rate',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Reimplementation of picked_rate''',
    'depends': [
        'stock',
        'purchase',
        'purchase_stock',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True
}
