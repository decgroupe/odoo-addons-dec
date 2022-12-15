{
    'name': 'MRP Production Request All',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Allow to create multiple manufacturing orders at once''',
    'depends': [
        'mrp',
        'mrp_production_request',
    ],
    'data': [
        'views/mrp_production_request.xml',
    ],
    'installable': True
}
