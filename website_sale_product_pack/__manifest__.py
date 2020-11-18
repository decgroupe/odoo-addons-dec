{
    'name': 'Website Sale Product Pack',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Allow public user to access product pack''',
    'depends': [
        'product',
        'product_pack',
    ],
    'data': ['security/website.xml'],
    'installable': True
}
