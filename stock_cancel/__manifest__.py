{
    'name': 'Stock Cancel',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Action to cancel stock moves recursively''',
    'depends': ['stock'],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'views/stock_move.xml',
        'views/stock_picking.xml',
    ],
    'installable': True
}
