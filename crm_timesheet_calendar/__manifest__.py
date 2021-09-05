{
    'name': 'CRM Timesheet Calendar',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add calendar view for CRM Timesheet lines",
    'depends': [
        'crm_timesheet',
        'hr_timesheet_calendar',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
