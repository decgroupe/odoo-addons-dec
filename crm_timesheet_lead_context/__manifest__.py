{
    'name': 'CRM Timesheet Calendar Lead Context',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Fix missing default project when creating an opportunity",
    'depends': [
        'crm_timesheet',
        'hr_timesheet_calendar',
        'project_crm_link',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
