{
    'name': 'HR Timesheet Auto-fill',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Fill data with previously entered values",
    'depends': ['hr_timesheet', ],
    'data': [
        'views/assets.xml',
        'views/account_analytic_line.xml',
    ],
    'installable': True
}
