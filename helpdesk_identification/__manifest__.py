{
    'name': 'Helpdesk (Identification)',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Customize name_search and add ticket informations",
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_partner_location',
    ],
    'data': ['views/helpdesk_ticket.xml', ],
    'installable': True
}
