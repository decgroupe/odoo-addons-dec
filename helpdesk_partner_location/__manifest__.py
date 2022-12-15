{
    'name': 'Helpdesk Partner Location',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Add partner location to tickets''',
    'depends': [
        'helpdesk_mgmt',
        'base_location',
    ],
    'data': ['views/helpdesk_ticket.xml', ],
    'installable': True
}
