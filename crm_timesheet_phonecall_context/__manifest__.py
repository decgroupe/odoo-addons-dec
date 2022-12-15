{
    'name': 'CRM Timesheet Phonecall Context',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Fix missing default project when creating a phonecall",
    'depends': [
        'crm_timesheet',
        'crm_phonecall_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',

    ],
    'installable': True
}
