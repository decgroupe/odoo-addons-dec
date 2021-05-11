{
    'name': 'Sale Partner State and Department',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'category': 'Sales',
    'summary': '''Add shipping partner state and department to sale orders''',
    'depends': [
        'sale_partner_location',
        'l10n_fr_base_location_department',
    ],
    'data':
        [
            'views/sale_order.xml',
        ],
    'installable': True
}
