{
    'name': 'Auth Unique Link',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "",
    'depends': [
        'web',
        'mail',
        # 'website',
    ],
    'data':
        [
            'security/res_groups.xml',
            'security/ir.model.access.csv',
            'data/ir_config_parameter.xml',
            'data/mail_template.xml',
            'templates/login_templates.xml',
            'views/assets.xml',
            'wizard/res_partner_impersonate.xml',
        ],
    'installable': True
}
