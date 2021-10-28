{
    'name': 'Software license',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Manage software licenses''',
    'depends': [
        'base',
        'mail',
        'product',
        'mrp',
        'software',
    ],
    "external_dependencies": {
        "python": ['semver'],
    },
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_tag.xml',
            'views/software_license.xml',
            'views/software_license_application.xml',
            'views/software_license_application_release.xml',
            'views/software_license_hardware.xml',
            'views/menu.xml',
        ],
    'installable': True
}
