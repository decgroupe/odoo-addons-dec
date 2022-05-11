{
    'name': 'Product Reference Market',
    'version': '12.0.3.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Product reference market management",
    'depends': ['product_reference_management', ],
    'data':
        [
            'security/model_security.xml',
            'security/ir.model.access.csv',
            'views/ref_market.xml',
            'views/menu.xml',
        ],
    'installable': True
}
