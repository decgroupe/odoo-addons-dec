{
    'name': 'Mail Activity Redirection',
    'summary': 'Redirect activities to specific users',
    'version': "13.0.1.0.0",
    'author': 'DEC, Odoo Community Association (OCA)',
    'category': 'Social Network',
    'website': 'https://github.com/OCA/social',
    'license': 'AGPL-3',
    'depends': ['mail', ],
    'data':
        [
            'security/ir.model.access.csv',
            'data/mail_activity_redirection.xml',
            'views/mail_activity_redirection.xml',
            'views/res_config_settings.xml',
        ],
    'installable': True
}
