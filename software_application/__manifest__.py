{
    'name': 'Software Application',
    'version': '12.0.3.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software applications",
    'depends': [
        'base',
        'mail',
        'product',
        'software',
    ],
    "external_dependencies": {
        "python": ['semver'],
    },
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_tag.xml',
            'views/software_application.xml',
            'views/software_application_release.xml',
            'views/menu.xml',
        ],
    'installable': True
}
