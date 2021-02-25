{
    'name': 'Mail Activity Redirection',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Customize activity targeted User with custom rules",
    'depends': [
        'mail',
        'base_xmlid',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'data/mail_activity_redirection.xml',
            'views/mail_activity_redirection.xml',
            'views/res_config_settings.xml',
        ],
    'installable': True
}
