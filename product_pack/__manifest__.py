{
    'name': 'Product Pack',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Product pack and kit management''',
    'depends': [
        'base',
        'product',
        'purchase',
        'sale',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/product_pack_purchaseline.xml',
        'views/product_pack_saleline.xml',
    ],
    'installable': True
}
