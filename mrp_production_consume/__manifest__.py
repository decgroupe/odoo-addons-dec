{
    'name': 'Manufacturing consume line',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Consume BoM line by line''',
    'depends': [
        'mrp',
        'sale_stock',
    ],
    'data': [
        'views/mrp_production.xml',
        'wizard/mrp_consume.xml',
    ],
    'installable': True
}
