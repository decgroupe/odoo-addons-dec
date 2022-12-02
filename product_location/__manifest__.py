{
    'name': 'Product Location',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add (Rack,Row,Case) fields to help locating a product in Warehouse''',
    'depends': ['product', ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'views/product_template.xml',
    ],
    'installable': True
}
