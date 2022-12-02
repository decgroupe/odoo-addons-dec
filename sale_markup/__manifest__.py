{
    'name': 'Sale Markup',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': "Adds the 'Markup' on sales order",
    'depends': [
        'sale_row_layout',
        'sale_margin',
    ],
    'data': ['views/sale_order.xml', ],
    'installable': True
}
