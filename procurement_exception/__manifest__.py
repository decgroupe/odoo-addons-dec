{
    'name': 'Procurement exception manager',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Create and customize activitiy redirection''',
    'depends': [
        'stock',
        'procurement_run_mto',
        'procurement_run_mts',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/ir.model.access.csv',
            'data/procurement_exception.xml',
            'views/procurement_exception.xml',
            'views/res_config_settings.xml',
        ],
    'installable': True
}
