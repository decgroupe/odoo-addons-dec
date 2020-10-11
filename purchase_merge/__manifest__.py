{
    'name': 'Purchase Merge',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Merge quotations''',
    'depends': [
        'purchase',
        'purchase_stock',
    ],
    'data': [
        'views/purchase_order.xml',
        'wizard/purchase_order_merge.xml',
    ],
    'installable': True
}
