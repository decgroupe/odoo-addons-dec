{
    'name': 'Production Partner Info',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Help to add fields related to partner like city",
    'depends': [
        'mrp',
        'mrp_stage',
        'base_location',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True
}
