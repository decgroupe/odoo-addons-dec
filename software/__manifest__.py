{
    'name': 'Software',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Software user groups''',
    'depends': [
        'dec',
    ],
    #'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/model_security.xml',
            'views/menu.xml',
        ],
    'installable': True
}
