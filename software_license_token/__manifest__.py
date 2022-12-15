{
    'name': 'Software License (token)',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software licenses (token)",
    'external_dependencies':
        {
            'python': [
                'Crypto',  # pip install pycryptodome
            ],
        },
    'depends': [
        'software_license_feature',
    ],
    'data':
        [
            'views/assets.xml',
            'views/software_license.xml',
            'views/software_license_hardware.xml',
            'views/software_application.xml',
        ],
    'installable': True
}
