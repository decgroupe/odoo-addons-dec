{
    'name': 'Procurement exception manager',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Create and customize activity redirection",
    'depends': [
        'stock',
        'procurement_log',
        'procurement_run_mto',
        'procurement_run_mts',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'data/procurement_exception.xml',
            'views/procurement_exception.xml',
            'views/res_config_settings.xml',
        ],
    'demo':
        [
            'demo/product_demo.xml',
        ],
        
    'installable': True
}
