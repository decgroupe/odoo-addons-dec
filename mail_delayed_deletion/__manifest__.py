{
    'name': 'Mail Delayed Deletion',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Deletion of an email will be delayed",
    'depends': ['mail', ],
    'data':
        [
            'views/mail_mail.xml',
            'data/ir_config_parameter.xml',
            'data/ir_cron.xml',
        ],
    'installable': True
}
