{
    'name': 'Tagging (product_reference)',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Tagging references models''',
    'depends': [
        'tagging',
        'product_reference',
    ],
    'data':
        [
            'views/tagging.xml',
            'views/ref_reference.xml',
            'views/ref_attribute.xml',
        ],
    'installable': True
}
