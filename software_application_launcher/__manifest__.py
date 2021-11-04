{
    'name': 'Software Application (launcher)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Launcher extra fields",
    'depends': [
        'software_application',
        'software_license',
        'website_sale', # for css styles
    ],
    'data':
        [
            'security/ir.model.access.csv',
            'views/software_application.xml',
            'views/software_application_image.xml',
        ],
    'installable': True
}
