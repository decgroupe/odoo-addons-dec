{
    'name': 'Partner Sale Dates',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'depends': [
        'sale',
        'sale_stock',
        'sale_delivery_date',
        'web_widget_remaining_days',
    ],
    'data': ['views/res_partner.xml', ],
    'installable': True
}
