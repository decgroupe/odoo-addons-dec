{
    'name': 'Sale Delivery Rate',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Reimplementation of delivery_rate''',
    'depends': [
        'sale',
        'sale_stock',
        'sale_timesheet',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True
}
