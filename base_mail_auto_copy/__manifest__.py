{
    'name': 'Mail Auto Copy',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin ',
    'website': 'https://www.decgroupe.com',
    'summary': '''Automatically add sender as Bcc''',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/ir_mail_server.xml',
        'views/res_users.xml',
    ],
    'installable': True
}
