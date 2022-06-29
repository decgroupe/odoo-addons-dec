{
    'name': 'Product Pricelist Analysis',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Show all pricelist items",
    'depends': [
        'product',
        'product_pricelist',
    ],
    'data':
        [
            'views/product_pricelist_item.xml',
            'views/product_pricelist.xml',
            'views/product_template.xml',
        ],
    'installable': True
}
