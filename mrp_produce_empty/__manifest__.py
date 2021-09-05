{
    'name': 'Manufacturing Produce Empty',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Allow to produce a product without initial raw moves''',
    'depends': [
        'mrp',
        'sale_stock',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
