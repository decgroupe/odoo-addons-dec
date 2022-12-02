{
    'name': 'Sale Row Layout',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': "Show line form product fields using a row",
    'depends': [
        'sale_margin'
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'views/assets.xml',
            'views/sale_order.xml',
        ],
    'installable': True
}
