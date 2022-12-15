{
    'name': 'Sale Partner Location',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': '''Add shipping partner location to sale orders''',
    'depends': [
        'sale',
        'base_location',
    ],
    'data':
        [
            'views/assets.xml',
            'views/sale_order.xml',
        ],
    'installable': True
}
