{
    'name': 'Software License (features)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Manage software licenses (features)''',
    'depends': [
        'software_license',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_license.xml',
            'views/software_license_feature.xml',
            'views/software_license_feature_property.xml',
            'views/software_license_feature_value.xml',
            'views/menu.xml',
        ],
    'installable': True
}
