{
    'name': 'Sale Warnings',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'category': 'Sales',
    'summary': '''Warnings on adding obsolete products to quotation''',
    'depends': [
        'mail',
        'sale',
        'product',
        'product_state_review',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        'data/mail_activity.xml',
        'data/mail_activity_template.xml',
    ],
    'installable': True
}
