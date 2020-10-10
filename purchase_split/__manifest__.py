{
    'name': 'Purchase Split',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Split a quotation by selecting lines to move''',
    'depends': [
        'purchase',
        'purchase_stock',
    ],
    'data': [
        'views/purchase_order.xml',
        'wizard/purchase_order_split.xml',
    ],
    'installable': True
}
