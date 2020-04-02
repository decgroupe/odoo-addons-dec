{
    'name': 'Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Get line infromations from procurement analysis''',
    'depends': [
        'mrp',
        'sale_stock',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
