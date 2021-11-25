{
    'name': 'Project Identification for Timesheet',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Add identification data from project",
    'depends': [
        'hr_timesheet',
        'project_identification',
    ],
    'data': ['views/account_analytic_line.xml', ],
    'installable': True
}
