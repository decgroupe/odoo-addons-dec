{
    'name': 'Product Template Link',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add a link to template from variant form''',
    'depends': [
        'product',
        'product_reference',
    ],
    # 'force_migration':'12.0.0.0.0',
    'data': [
        'views/assets.xml',
        'views/product_product.xml',
    ],
    'installable': True
}
