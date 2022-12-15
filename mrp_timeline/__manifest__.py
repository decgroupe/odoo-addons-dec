{
    'name': 'Manufacturing timeline',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Timeline view for production",
    'depends': [
        'mrp',
        'mrp_bom_supplier',
        'web_timeline',
    ],
    "data": [
        "templates/assets.xml",
        "views/mrp_production.xml",
    ],
    'installable': True
}
