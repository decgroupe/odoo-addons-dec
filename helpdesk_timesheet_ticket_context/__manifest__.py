{
    'name': 'Helpdesk Timesheet Ticket Context',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Fix missing default project when creating a ticket",
    'depends': [
        'helpdesk_mgmt_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',

    ],
    'installable': True
}
