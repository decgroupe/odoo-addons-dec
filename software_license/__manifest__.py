{
    'name': 'Software License',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software licenses",
    'depends': [
        'software_application',
        'mrp',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_license.xml',
            'views/software_application.xml',
            'views/software_license_hardware.xml',
            'views/menu.xml',
        ],
    'installable': True
}
