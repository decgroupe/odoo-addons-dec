{
    'name': 'Software License (pass)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software licenses (pass)",
    'depends': [
        'base_location',
        'software_license_feature',
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_license_pass.xml',
            'views/software_license.xml',
            # 'views/software_license_application.xml',
            # 'views/software_license_hardware.xml',
            'views/software_license_pack.xml',
            'views/software_license_pack_line.xml',
            'views/menu.xml',
            'data/sequence.xml',
            'data/mail_jinja.xml',
        ],
    'installable': True
}
