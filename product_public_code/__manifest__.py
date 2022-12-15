{
    'name': 'Product Public Code',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add public code on product form''',
    'depends': [
        'product',
        'sale',
    ],
    'data':
        [
            'views/product_template.xml',
            'views/product_product.xml',
        ],
    'installable': True
}
