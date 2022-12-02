{
    'name': 'Manufacturing Product Location on Consume Line',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Display the production stock location for each line",
    'depends': [
        'mrp_production_consume',
        'product_location',
    ],
    'data': [
        'views/assets.xml',
        'wizard/mrp_consume.xml',
    ],
    'installable': True
}
