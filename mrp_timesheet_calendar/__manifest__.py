{
    'name': 'Manufacturing Timesheet Calendar',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Add production name on calendar view",
    'depends': [
        'hr_timesheet_calendar',
        'mrp_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',
    ],
    'installable': True
}
