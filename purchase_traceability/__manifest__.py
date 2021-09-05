{
    'name': 'Purchase Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Show related sale lines on purchase form''',
    'depends': [
        'purchase',
        'sale_purchase',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/purchase_order.xml',
        ],
    'installable': True
}
