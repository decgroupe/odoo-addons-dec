{
    'name': 'Purchase Picking Link',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Show related outgoing pickings on purchase form''',
    'depends': [
        'purchase_stock',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/purchase_order.xml',
        ],
    'installable': True
}
