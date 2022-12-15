{
    'name': 'Manufacturing Partner Academy',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add partner academy to production orders''',
    'depends': [
        'mrp_partner',
        'partner_academy',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
