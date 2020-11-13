{
    'name': 'Product Small Supply',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': 'Small supply is a new consumable definition',
    'depends': [
        'product',
        'stock',
        'product_legacy_availability',
    ],
    'data': [
        'views/product_template.xml',
        'views/product_product.xml',
    ],
    'installable': True
}
