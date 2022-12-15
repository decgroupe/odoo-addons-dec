{
    'name': 'Purchase pricelists',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Use same pricelist model for sale and purchase''',
    'depends': [
        'product',
        'purchase',
        'sale',
        'product_pricelist_supplierinfo',
    ],
    'data':
        [
            'security/purchase_pricelist.xml',
            'views/product_pricelist.xml',
            'views/purchase_order.xml',
            'views/res_partner.xml',
            'views/menu.xml',
        ],
    'installable': True
}
