{
    'name': 'Production Partner Info',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add fields related to partner like city''',
    'depends': [
        'mrp',
        'base_location',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
