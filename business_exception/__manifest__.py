{
    'name': 'Business exception manager',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Intercept business methods to customize activitiy "
        "redirection",
    'depends':
        [
            'mail',
            'mrp',
            'stock',
            'purchase_stock',
            'sale_purchase',
            'sale_stock',
        ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/ir.model.access.csv',
            'data/business_exception.xml',
            'views/business_exception.xml',
            'views/res_config_settings.xml',
        ],
    'installable': True
}
