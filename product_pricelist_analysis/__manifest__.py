{
    'name': 'Product Pricelist Analysis',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Show all pricelist items",
    'depends': [
        'product',
        'product_pricelist',
        'purchase_pricelist', # Needed for type sale/purchase
    ],
    'data':
        [
            'views/product_pricelist_item.xml',
            'views/product_pricelist.xml',
            'views/product_template.xml',
        ],
    'installable': True
}
