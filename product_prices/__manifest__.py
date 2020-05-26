{
    'name': 'Product prices',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Store prices write dates''',
    'depends': [
        'product',
        'product_seller',
        'product_pricelist',
    ],
    'data':
        [
            'views/product_template.xml',
        ],
    'installable': True
}
