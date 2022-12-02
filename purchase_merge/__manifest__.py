{
    'name': 'Purchase Merge',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Merge quotations''',
    'depends': [
        'purchase',
        'purchase_stock',
        'purchase_line_procurement_group',
    ],
    'data': [
        'views/purchase_order.xml',
        'views/template.xml',
        'wizard/purchase_order_merge.xml',
    ],
    'installable': True
}
