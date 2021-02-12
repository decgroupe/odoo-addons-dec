{
    'name': 'Product Prices History',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Store prices based on pricelist",
    'depends': ['product_prices', ],
    'data': [
        'data/ir_cron.xml',
        'views/product_computed_price_history.xml',
    ],
    'installable': True
}
