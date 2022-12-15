{
    'name': 'Helpdesk Sale',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Create sale order from Ticket''',
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_references',
        'sale_summary',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        "views/helpdesk_ticket.xml",
    ],
    'installable': True
}
