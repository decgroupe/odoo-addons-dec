{
    'name': 'Product Favorite Ok',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        'Set favorite_ok if product has already been used in a sale order or '
        'a purchase order or as a component of a bill of material',
    'depends': [
        'mrp',
        'product_autoset_ok',
    ],
    'data': ['views/product_template.xml'],
    'installable': True
}
