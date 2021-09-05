{
    'name': 'Manufacturing (BoM Product State)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add product state as a BoM field",
    'depends': [
        'mrp',
        'product_state_review',
    ],
    'data': [
        'views/mrp_bom.xml',
    ],
    'installable': True
}
