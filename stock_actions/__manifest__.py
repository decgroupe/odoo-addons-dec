{
    'name': 'Stock Actions',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Public methods to control stock moves",
    'depends': ['stock'],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'views/stock_move.xml',
        'views/stock_picking.xml',
    ],
    'installable': True
}
