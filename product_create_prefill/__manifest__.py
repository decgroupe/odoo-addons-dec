{
    'name': 'Product Create Prefill',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': 'Use webscrapper to pre-fill product data',
    'depends': [
        'product',
        'sale',
    ],
    "external_dependencies": {
        "python": [
            'jsoncomment',
            'fake-useragent',
            'pyquery',
            'parse',
            'w3lib',
        ],
    },
    'data': [],
    'installable': True
}
