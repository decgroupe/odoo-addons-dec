{
    'name': 'Manufacturing Partner Location',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add partner location to production orders''',
    'depends': [
        'mrp_partner',
        'base_location',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
