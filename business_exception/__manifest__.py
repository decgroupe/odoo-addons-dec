{
    'name': 'Business exception manager',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Intercept business methods to customize activitiy "
        "redirection",
    'depends':
        [
            'mrp',
            'stock',
            'purchase_stock',
            'sale_purchase',
            'sale_stock',
        ],
    #'force_migration':'12.0.0.0.0',
    'data': [],
    'installable': True
}
