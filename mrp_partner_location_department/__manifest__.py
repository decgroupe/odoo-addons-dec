{
    'name': 'Manufacturing Partner State and Department',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add partner state and department to production orders''',
    'depends': [
        'mrp_partner_location',
        'l10n_fr_base_location_department',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
