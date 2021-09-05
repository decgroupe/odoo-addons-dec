{
    'name': 'Product pricelist sequence',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Sequence field added to pricelist to customize rule priority''',
    'depends': [
        'product',
    ],
    'data':
        [
            'views/product_pricelist.xml',
            'views/product_pricelist_item.xml',
        ],
    'installable': True
}
