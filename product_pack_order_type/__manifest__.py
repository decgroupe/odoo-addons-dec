{
    'name': 'Product Pack Order Type',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Assign pack for sale-only / purchase-only''',
    'depends': [
        'product_pack',
        'sale_product_pack',
        'purchase_product_pack',
    ],
    'data': ['views/product_template.xml', ],
    'installable': True
}
