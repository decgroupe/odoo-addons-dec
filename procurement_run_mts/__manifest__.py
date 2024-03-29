{
    'name': 'Procurement Run MTS',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Scheduler task extended to validate make_to_stock moves''',
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
