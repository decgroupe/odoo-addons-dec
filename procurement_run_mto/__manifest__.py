{
    'name': 'Procurement Run',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Scheduler task extended to re-create PO/MO''',
    'depends': [
        'stock',
        'mrp',
        'purchase_stock',
    ],
    'data':
        [
            'views/procurement.xml',
        ],
    'installable': True
}
