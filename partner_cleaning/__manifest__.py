{
    'name': 'Partner Cleaning',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Auto delete users and partners created by spammers",
    'depends': [
        "base",
        "auth_signup",
    ],
    'data': ['data/ir_cron.xml', ],
    'installable': True
}
