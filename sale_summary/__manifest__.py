{
    'name': 'Sale Summary',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': '''Add summary field on sale order''',
    'depends': ['sale', ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'views/assets.xml',
        'views/sale_order.xml',
    ],
    'installable': True
}
