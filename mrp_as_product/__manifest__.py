{
    'name': 'Product From Manufacturing',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Shortcuts to products from bill of materials or "
        "production order",
    'depends': [
        'product',
        'product_action_view',
        'mrp',
    ],
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
