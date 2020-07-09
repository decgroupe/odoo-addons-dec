{
    'name': 'Product pricelist analysis',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Show all pricelist items''',
    'depends': [
        'product',
        'product_pricelist',
        'dec',
    ],
    'data':
        [
            'views/product_pricelist_item.xml',
            'views/product_pricelist.xml',
            'views/product_template.xml',
            'views/menu.xml',
        ],
    'installable': True
}
