{
    'name': 'Product Prices History',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Store prices based on pricelist",
    'depends': ['product_prices', ],
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/product_prices_history.xml',
        'views/product_template.xml',
    ],
    'installable': True
}
