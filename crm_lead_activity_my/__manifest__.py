{
    'name': 'CRM My Activities',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Backport next activity workflow from Odoo 14.0 but use current"
        "user",
    'depends':
        [
            'crm',
            'web_widget_mail_list_activity',
            'web_widget_remaining_days',
            'mail_activity_my',
        ],
    'data': ['views/crm_lead.xml', ],
    'installable': True
}
