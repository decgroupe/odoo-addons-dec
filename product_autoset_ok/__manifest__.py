{
    'name': 'Product Autoset Ok',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        'Set sale_ok if product has already been used in a sale order or '
        'set purchase_ok if product has already been used in a purchase order',
    'depends': [
        'product',
        'sale',
    ],
    'data': ['data/ir_cron.xml', ],
    'installable': True
}
