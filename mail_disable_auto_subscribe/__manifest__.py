{
    'name': 'Mail Disable Auto Subscribe',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add UI settings to disable auto-subscribe with @-mention",
    'depends': ['mail', ],
    'data': [
        'views/mail_message_subtype.xml',
        'views/res_users.xml',
    ],
    'installable': True
}
