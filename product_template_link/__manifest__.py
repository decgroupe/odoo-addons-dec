{
    'name': 'Product Template Link',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add a link to template from variant form''',
    'depends': [
        'product',
    ],
    'data': [
        'views/assets.xml',
        'views/product_product.xml',
    ],
    'installable': True # deprecated via "product_action_view"
}
