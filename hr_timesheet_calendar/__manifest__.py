{
    'name': 'HR Timesheet Calendar',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add calendar view for Timesheet lines",
    'depends': [
        'hr_timesheet',
        'project_timesheet_time_control'
    ],
    'data': [
        'views/account_analytic_line.xml',

    ],
    'installable': True
}
