{
    'name': 'Manufacturing Traceability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Get line informations from procurement analysis''',
    'depends': [
        'product',
        'mrp',
        'sale_stock',
        'purchase_stock',
        'stock_traceability',
        'stock_orderpoint_traceability',
        'stock_mrp_traceability',
    ],
    'data': [
        'views/assets.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
