{
    'name': 'Purchase Split',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Split a quotation by selecting lines to move''',
    'depends': [
        'purchase',
        'purchase_stock',
    ],
    'data': [
        'views/purchase_order.xml',
        'wizard/purchase_order_split.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
