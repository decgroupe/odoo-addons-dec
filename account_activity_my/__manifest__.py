{
    'name': 'Account My Activities',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Backport next activity workflow from Odoo 14.0 but use current"
        "user",
    'depends':
        [
            'account',
            'web',
            'mail_activity_my',
        ],
    'data': ['views/account_invoice.xml', ],
    'installable': True
}
