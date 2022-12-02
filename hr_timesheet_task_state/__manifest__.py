{
    'name': 'HR Timesheet Task State',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Set task state when creating it for a Timesheet",
    'depends': [
        'hr_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',

    ],
    'installable': True
}
