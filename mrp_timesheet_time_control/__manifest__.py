{
    'name': 'Manufacturing Timesheet Time Control',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Exact start time for a timesheet line",
    'depends': [
        'mrp_timesheet',
        'project_timesheet_time_control',
    ],
    'data': [
        'views/mrp_production.xml',

    ],
    'installable': True
}
