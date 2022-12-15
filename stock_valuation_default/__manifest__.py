{
    'name': 'Stock Valuation Default',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Remove default value otherwise category valuation property "
        "will never be taken into account",
    'depends': ['stock_account', ],
    'data': ['views/product_template.xml', ],
    'installable': True
}
