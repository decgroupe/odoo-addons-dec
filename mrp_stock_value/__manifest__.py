{
    'name': 'Manufacturing Stock Value',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Show consummed value",
    'depends': [
        'mrp',
        'product_prices_history',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable': True
}
