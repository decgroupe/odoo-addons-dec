{
    'name': 'Product legacy availability',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Forward port of legacy procure and supply methods''',
    'depends': [
        'product',
        'stock',
    ],
    'data':
        [
            'views/product_template.xml',
            'views/product_product.xml',
        ],
    'installable': True
}
