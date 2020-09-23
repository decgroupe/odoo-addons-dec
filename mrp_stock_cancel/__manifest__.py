{
    'name':
        'Manufacturing Stock Cancel',
    'version':
        '12.0.1.0.0',
    'author':
        'DEC, Yann Papouin',
    'website':
        'http://www.dec-industrie.com',
    'summary':
        '''Allow to cancel a stock move from a production order when unlocked''',
    'depends': [
        'mrp',
        'sale_stock',
        'stock_cancel',
    ],
    'data': ['views/mrp_production.xml', ],
    'installable':
        True
}
