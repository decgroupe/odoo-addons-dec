{
    'name': 'Software License (legacy)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Legacy fields''',
    'depends': [
        'software_license_feature',
        'software_license_dongle',
    ],
    'data':
        [
            'data/software_license_feature.xml',
            'views/software_license.xml',
        ],
    'installable': True
}
