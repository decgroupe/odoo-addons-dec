{
    'name': 'Sale Software License (pass)',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Manage software licenses (pass)",
    'depends': [
        'sale_timesheet',
        'software_license_pass',
    ],
    'data':
        [
            'views/software_license_pass.xml',
            'views/product_template.xml',
            'views/sale_order.xml',
            'data/mail_template.xml',
        ],
    'installable': True
}
