{
    'name': 'Helpdesk Partner State and Department',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add partner state and department to tickets''',
    'depends': [
        'helpdesk_partner_location',
        'l10n_fr_base_location_department',
    ],
    'data': ['views/helpdesk_ticket.xml', ],
    'installable': True
}
