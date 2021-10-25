{
    'name': 'Software License (launcher)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Launcher extra fields",
    'depends': [
        'software_license',
        'website_sale', # for css styles
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_license_application.xml',
            'views/software_license_application_image.xml',
        ],
    'installable': True
}
