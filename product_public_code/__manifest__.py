{
    'name': 'Product Public Code',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
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
