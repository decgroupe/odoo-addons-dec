{
    'name': 'Helpdesk References',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': '''Link helpdesk ticket with sale, manufacturing, project, etc.''',
    'depends': [
        'helpdesk_mgmt',
    ],
    #'force_migration':'12.0.0.0.0',
    'data': [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_reference.xml",
        "views/helpdesk_ticket.xml",
    ],
    'installable': True
}
