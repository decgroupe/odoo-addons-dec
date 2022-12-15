{
    'name': 'Manufacturing (BoM order)',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Production order''',
    'depends': ['mrp', ],
    'data': [
        'views/mrp_production.xml',
        'views/mrp_bom.xml',
    ],
    'installable': True
}
