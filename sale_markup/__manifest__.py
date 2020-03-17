{
    'name': 'Sale markup',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'category': 'Sales',
    'summary': '''Adds the 'Markup' on sales order''',
    'depends': [
        'dec',
        'sale_margin'
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            # 'security/model_security.xml',
            'views/assets.xml',
            'views/sale_order_views.xml',
        ],
    'installable': True
}
