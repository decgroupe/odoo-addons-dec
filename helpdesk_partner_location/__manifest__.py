{
    'name': 'Helpdesk Partner Location',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Add partner location to tickets''',
    'depends': [
        'helpdesk_mgmt',
        'base_location',
    ],
    'data': ['views/helpdesk_ticket.xml', ],
    'installable': True
}
