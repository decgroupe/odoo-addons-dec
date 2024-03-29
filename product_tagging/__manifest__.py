{
    'name': 'Tagging (products)',
    'version': '12.0.1.0.2',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Tagging products''',
    'depends': [
        'tagging',
        'product',
    ],
    'data': [
        'views/tagging.xml',
        'views/product.xml',
    ],
    'installable': True,
    # 'force_migration': '12.0.0.0.0',
}
