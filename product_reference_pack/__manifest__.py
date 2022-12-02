{
    'name': "Product's Pack Reference",
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Pack reference management",
    'depends': [
        'product_public_code',
        'product_reference_management',
        'product_pack_order_type',
    ],
    'data':
        [
            'security/model_security.xml',
            'security/ir.model.access.csv',
            'views/product_template.xml',
            'views/ref_pack.xml',
            'views/menu.xml',
        ],
    'installable': True
}
