{
    'name': 'Procurement Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add procurement view to track moves''',
    'depends': [
        'stock',
        'sale_stock',
        'purchase_stock',
        'mrp',
    ],
    'data':
        [
            'views/procurement.xml',
            'views/menu.xml',
        ],
    'installable': True
}
