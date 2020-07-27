{
    'name': 'Manufacturing (BoM prices)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Get sell and cost price''',
    'depends': [
        'mrp',
        'mrp_bom_supplier',
        'product_prices',
    ],
    'data': [
        'views/mrp_bom.xml',
    ],
    'installable': True
}
