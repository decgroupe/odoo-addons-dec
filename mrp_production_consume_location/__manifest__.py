{
    'name': 'Manufacturing Product Location on Consume Line',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
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
