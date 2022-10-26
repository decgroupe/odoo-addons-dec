{
    'name': 'User Login Sync',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Base',
    'summary': "Keep user login in sync with contact e-mail",
    'depends': [
        'base',
        'mail_qweb',
    ],
    'data':
        [
            'security/res_groups.xml',
            'views/res_partner_template.xml',
            'data/ir_ui_view.xml',
            'data/mail_template.xml',
        ],
    'installable': True
}
