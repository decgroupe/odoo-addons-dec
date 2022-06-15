{
    'name': 'Auth Local Password',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow use of a seconday password (PIN) when local",
    'depends': [
        'web',
        'mail',
    ],
    'data': [
        'security/res_groups.xml',
        'views/res_users.xml',
    ],
    'installable': True
}
