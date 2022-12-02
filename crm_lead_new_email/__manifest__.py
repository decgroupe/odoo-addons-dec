{
    'name': 'CRM New Lead Email',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Send an e-mail when a new lead is created",
    'depends': ['crm', ],
    'data': [
        'data/mail_template.xml',
        'data/base_automation.xml',
    ],
    'installable': True
}
