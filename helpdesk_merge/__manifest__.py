{
    'name': 'Merge Helpdesk Tickets',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin ',
    'website': 'https://www.decgroupe.com',
    'depends': [
        'helpdesk_mgmt',
        'deltatech_merge',
    ],
    'data': [
        'security/res_groups.xml',
        'wizard/merge_helpdesk_ticket.xml',
    ],
    'installable': True
}
