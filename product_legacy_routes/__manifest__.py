{
    'name': 'Product legacy routes',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Forward port of legacy procure and supply methods''',
    'depends': [
        'stock',
        'purchase_stock',
        'mrp',
        'stock_mts_mto_rule',
    ],
    'data':
        [
            'views/product_template.xml',
        ],
    'installable': True
}
