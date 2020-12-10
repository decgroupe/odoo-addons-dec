{
    'name': 'Easy expense sheet (HE)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Fill expense sheet with an inline mode",
    'depends': [
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_sheet.xml',
        'data/product_category.xml',
        'data/product_product.xml',
    ],
    'installable': True
}
