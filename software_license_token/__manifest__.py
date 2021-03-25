{
    'name': 'Software License (token)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Manage software licenses (token)''',
    'external_dependencies':
        {
            'python': [
                'Crypto',  # pip install pycryptodome
            ],
        },
    'depends': [
        'portal',
        'software_license_feature',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'security/software_license.xml',
            'views/assets.xml',
            'views/software_license.xml',
            'views/software_license_hardware.xml',
            'views/software_license_application.xml',
            'templates/software_license.xml',
        ],
    'installable': True
}
