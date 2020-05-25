{
    'name': 'Product legacy routes',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Forward port of legacy procure and supply methods''',
    'depends': [
        'stock',
        'purchase_stock',
        'mrp',
    ],
    'data':
        [
            'views/product_template.xml',
        ],
    'installable': True
}
