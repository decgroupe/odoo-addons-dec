{
    'name': 'Product Template Link',
    'version': '12.0.1.0.0',
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
    'installable': False # deprecated via "product_action_view"
}
