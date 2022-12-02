{
    'name': 'Helpdesk Identification for Timesheet',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add identification data from helpdesk",
    'depends': [
        'hr_timesheet',
        'helpdesk_identification',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
