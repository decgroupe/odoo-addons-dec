{
    'name': 'Manufacturing (transtion)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Transition only''',
    'depends': [
        'mrp',
        'stock',
        'stock_mrp_traceability',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
