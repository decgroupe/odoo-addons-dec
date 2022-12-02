{
    'name': 'Website Sale Product Pack',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Allow public user to access product pack''',
    'depends': [
        'product',
        'product_pack',
    ],
    'data': ['security/website.xml'],
    'installable': True
}
