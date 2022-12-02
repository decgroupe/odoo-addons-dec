{
    'name': 'Mail QWeb',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Default templates",
    # TODO: rewrite templates of message_notification_email/mail_notification_light from odoo/addons/mail/data/mail_data.xml
    'depends': [
        'mail',
        'mail_inline_css',
        'email_template_qweb',
        'partner_company_type',
    ],
    'data': ['data/ir_ui_view.xml', ],
    'installable': True
}
