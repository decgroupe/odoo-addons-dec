{
    'name': 'Software License (GitLab)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Store GitLab project infos to applications",
    'depends': [
        'software_license',
        'connector_gitlab',
    ],
    'data':
        [
            'views/software_application.xml',
        ],
    'installable': True
}
