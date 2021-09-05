{
    'name': 'Account Partner State and Department',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add partner state and department to invoices and "
        "accounting lines",
    'depends':
        [
            'account_partner_location',
            'l10n_fr_base_location_department',
        ],
    'data': ['views/account_invoice.xml', ],
    'installable': True
}
