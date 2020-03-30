{
    'name': 'Stock Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Get move final location from any move of the chain''',
    'depends': [
        'stock',
        'sale_stock',
        'purchase_stock',
    ],
    'data':
        [
            'views/procurement.xml',
        ],
    'installable': True
}
