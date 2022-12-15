{
    'name': 'Software License (keygen)',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Key generator''',
    'external_dependencies':
        {
            'python':
                [
                    'key_generator',  # pip install key-generator
                    'Crypto',  # pip install pycryptodome
                ],
        },
    'depends': ['software_license', ],
    'data':
        [
            'views/software_license.xml',
            'views/software_application.xml',
        ],
    'installable': True
}
