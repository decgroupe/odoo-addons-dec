{
    'name': 'Software License (Portal)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Manage software licenses through the portal''',
    'depends': [
        'portal',
        'software_license_token',
        'software_license_dongle',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'security/software_license.xml',
            'views/software_license_application.xml',
            'templates/software_license.xml',
        ],
    'installable': True
}
