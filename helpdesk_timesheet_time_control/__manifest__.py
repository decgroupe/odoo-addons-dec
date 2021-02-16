{
    'name': 'Helpdesk Timesheet Time Control',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary':
        "Exact start time for a timesheet line",
    'depends': [
        'helpdesk_mgmt_timesheet',
        'project_timesheet_time_control',
    ],
    'data': [
        'views/helpdesk_ticket.xml',

    ],
    'installable': True
}
