{
    'name': 'Software License Location',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add shipping partner location to licenses",
    'depends': [
        'base_location',
        'software_license',
    ],
    'data': ['views/software_license.xml', ],
    'installable': True
}
