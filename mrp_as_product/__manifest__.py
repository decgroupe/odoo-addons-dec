{
    'name': 'Product From Manufacturing',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Shortcuts to products from bill of materials or "
        "production order",
    'depends': [
        'product',
        'mrp',
    ],
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_production.xml',
    ],
    'installable': True
}
