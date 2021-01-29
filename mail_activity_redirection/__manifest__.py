{
    'name': 'Mail Activity Redirection',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Customize activitiy targeted User with custom rules",
    'depends': ['mail', ],
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
