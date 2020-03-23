{
    'name': 'Software license',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Manage software licenses (serial, dongle)''',
    'depends': [
        'base',
        'product',
        'mrp',
        'software',
    ],
    'force_migration':'12.0.0.0.0',
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_license.xml',
            'views/software_license_application.xml',
            'views/menu.xml',
            'report/software_license.xml',
        ],
    'installable': True
}
