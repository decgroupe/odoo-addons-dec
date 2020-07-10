{
    'name': 'Purchase Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Show related orderpoint on purchase form''',
    'depends': [
        'purchase'
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/purchase_order.xml',
        ],
    'installable': True
}
