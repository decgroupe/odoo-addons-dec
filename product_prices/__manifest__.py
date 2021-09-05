{
    'name': 'Product prices',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Store prices write dates''',
    'depends': [
        'web_widget_mermaid',
        'product',
        'product_seller',
        'product_pricelist',
    ],
    'data':
        [
            'views/assets.xml',
            'views/product_template.xml',
            'wizard/product_price_graph.xml',
        ],
    'installable': True
}
