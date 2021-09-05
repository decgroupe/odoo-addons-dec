{
    'name': 'Product Template Orderpoints',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow to filter product based on orderpoints status",
    'depends': [
        'product',
        'stock',
    ],
    'data':
        [
            'views/product.xml',
        ],
    'installable': True
}
