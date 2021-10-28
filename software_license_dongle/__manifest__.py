{
    'name': 'Software License (dongle)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software licenses (dongle)",
    'depends': [
        'software_license',
    ],
    'data':
        [
            'views/software_application.xml',
            'views/software_license.xml',
            'views/software_license_hardware.xml',
        ],
    'installable': True
}
